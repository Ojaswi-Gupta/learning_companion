
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

    let uploadBtn = document.querySelector(".sidebar button")
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
    }
}



async function send(){

    let input = document.getElementById("msg")
    let msg = input.value.trim()

    if(!msg) return

    addMessage(msg, "user")

    input.value = ""

    let thinking = addMessage("Thinking...", "ai")

    try {
        let res = await fetch(API + "/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Session-ID": sessionId
            },
            body: JSON.stringify({ query: msg })
        })

        // Store session ID from response
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

                btn.innerText = "Thinking..."
                btn.disabled = true

                try {
                    let r = await fetch(API + "/general", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ query: msg })
                    })

                    if (!r.ok) {
                        let err = await r.json()
                        addMessage("Error: " + (err.detail || "General AI failed"), "ai")
                        btn.remove()
                        return
                    }

                    let d = await r.json()

                    addMessage(d.response, "ai")

                    btn.remove()
                } catch (e) {
                    addMessage("Could not connect to server", "ai")
                    btn.innerText = "Ask General AI"
                    btn.disabled = false
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

            el.innerHTML = `
<span>${d.name}</span>
<button onclick="delDoc('${id}')">Delete</button>
`

            div.appendChild(el)
        }
    } catch (e) {
        console.error("loadDocs error:", e)
    }
}



async function delDoc(id){

    try {
        let res = await fetch(API + "/documents/" + id, {
            method: "DELETE"
        })

        if (!res.ok) {
            alert("Failed to delete document")
            return
        }

        loadDocs()
    } catch (e) {
        alert("Could not connect to server")
        console.error("Delete error:", e)
    }
}



loadDocs()