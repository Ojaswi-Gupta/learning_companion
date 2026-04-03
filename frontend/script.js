
// Set API URL: override via window.API_URL or default to localhost for dev
const API = window.API_URL || "http://127.0.0.1:8000"

let sessionId = localStorage.getItem("sessionId") || ""

console.log("SCRIPT LOADED")

async function upload(){
    let file = document.getElementById("fileUpload").files[0]
    if(!file){
        alert("Choose a file")
        return
    }

    let form = new FormData()
    form.append("file", file)

    let uploadBtn = document.querySelector(".upload-group button") || document.querySelector(".sidebar button")
    uploadBtn.disabled = true
    uploadBtn.innerText = "Uploading..."

    try {
        let res = await fetch(API + "/upload", {
            method: "POST",
            body: form
        })

        if (!res.ok) {
            let err = await res.json()
            alert(err.detail || "Upload failed")
            return
        }
        loadDocs()
    } catch (e) {
        alert("Could not connect to server")
        console.error("Upload error:", e)
    } finally {
        uploadBtn.disabled = false
        uploadBtn.innerText = "Upload"
        // Clear input to allow uploading again easily
        document.getElementById("fileUpload").value = ""
    }
}

// Replaces standard "Thinking..." with CSS animated dots
function addTypingIndicator() {
    let box = document.getElementById("chatbox")
    let div = document.createElement("div")
    div.className = "typing-indicator"
    div.innerHTML = `<span></span><span></span><span></span>`
    box.appendChild(div)
    box.scrollTop = box.scrollHeight
    return div
}

async function send(){
    let input = document.getElementById("msg")
    let msg = input.value.trim()

    if(!msg) return

    addMessage(msg, "user")
    input.value = ""

    // Use animated typing dots instead of raw text
    let thinking = addTypingIndicator()

    try {
        let res = await fetch(API + "/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Session-ID": sessionId
            },
            body: JSON.stringify({ query: msg })
        })

        let sid = res.headers.get("X-Session-ID")
        if (sid) {
            sessionId = sid
            localStorage.setItem("sessionId", sid)
        }

        if (!res.ok) {
            thinking.remove()
            let err = await res.json()
            addMessage("Error: " + (err.detail || "Something went wrong"), "ai")
            return
        }

        let data = await res.json()
        console.log("API RESPONSE:", data)

        thinking.remove()
        let aiDiv = addMessage(data.response, "ai")

        if(data.fallback){
            let btn = document.createElement("button")
            btn.innerText = "Ask General AI"
            btn.style.marginTop = "10px"
            
            btn.onclick = async () => {
                btn.style.display = "none" // Instantly hide button when clicked
                let fallbackThinking = addTypingIndicator()
                
                try {
                    let r = await fetch(API + "/general", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ query: msg })
                    })

                    fallbackThinking.remove()
                    if (!r.ok) {
                        let err = await r.json()
                        addMessage("Error: " + (err.detail || "General AI failed"), "ai")
                        btn.style.display = "block" // Re-show on failure
                        return
                    }

                    let d = await r.json()
                    addMessage(d.response, "ai")
                    btn.remove()
                } catch (e) {
                    fallbackThinking.remove()
                    addMessage("Could not connect to server", "ai")
                    btn.style.display = "block"
                    console.error("General AI error:", e)
                }
            }
            document.getElementById("chatbox").appendChild(btn)
        }
    } catch (e) {
        thinking.remove()
        addMessage("Could not connect to server", "ai")
        console.error("Chat error:", e)
    }
}

function addMessage(text, type){
    let box = document.getElementById("chatbox")
    let div = document.createElement("div")
    div.className = "message " + type
    div.innerHTML = marked.parse(text)
    box.appendChild(div)
    box.scrollTop = box.scrollHeight
    return div
}

async function loadDocs(){
    try {
        let res = await fetch(API + "/documents")
        if (!res.ok) {
            console.error("Failed to load documents")
            return
        }
        let docs = await res.json()
        let div = document.getElementById("docs")
        div.innerHTML = ""

        for(let id in docs){
            let d = docs[id]
            let el = document.createElement("div")
            el.className = "docItem"
            el.id = `doc-${id}`
            
            // Pass 'this' so we can immediately fade out the specific row
            el.innerHTML = `
                <span>${d.name}</span>
                <button onclick="delDoc('${id}', this.parentElement)">Delete</button>
            `
            div.appendChild(el)
        }
    } catch (e) {
        console.error("loadDocs error:", e)
    }
}

// Now includes 'element' to allow Optimistic UI instant removal
async function delDoc(id, element){
    // Optimistic UI: Immediately hide the list item to make UI feel instant
    if (element) {
        element.style.opacity = '0.5';
        element.style.pointerEvents = 'none';
        element.querySelector('button').innerText = "..."
    }

    try {
        let res = await fetch(API + "/documents/" + id, {
            method: "DELETE"
        })

        if (!res.ok) {
            alert("Failed to delete document")
            if (element) {
                element.style.opacity = '1';
                element.style.pointerEvents = 'all';
                element.querySelector('button').innerText = "Delete"
            }
            return
        }

        // Finish Optimistic UI by sliding out the element
        if (element) {
            element.style.display = 'none';
        }
        loadDocs() // Sync accurately in background
    } catch (e) {
        alert("Could not connect to server")
        if (element) {
            element.style.opacity = '1';
            element.style.pointerEvents = 'all';
            element.querySelector('button').innerText = "Delete"
        }
        console.error("Delete error:", e)
    }
}

// Allow pressing "Enter" on keyboard to send message
document.addEventListener("DOMContentLoaded", () => {
    let msgInput = document.getElementById("msg");
    if (msgInput) {
        msgInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                send();
            }
        });
    }
});

loadDocs()