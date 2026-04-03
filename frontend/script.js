// Set API URL: override via window.API_URL or default to localhost for dev
const API = window.API_URL || "http://127.0.0.1:8000"

let sessionId = localStorage.getItem("sessionId") || ""

console.log("SCRIPT LOADED")

// ===== Upload =====

function setupDropzone() {
    const dropzone = document.getElementById("dropzone")
    const fileInput = document.getElementById("fileUpload")
    if (!dropzone || !fileInput) return

    // Show file name when selected
    fileInput.addEventListener("change", () => {
        if (fileInput.files[0]) {
            const name = fileInput.files[0].name
            dropzone.querySelector(".upload-text").textContent = name
            dropzone.querySelector(".upload-hint").textContent = "Click Upload to proceed"
        }
    })

    // Drag & drop visuals
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault()
        dropzone.classList.add("dragover")
    })
    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover")
    })
    dropzone.addEventListener("drop", (e) => {
        e.preventDefault()
        dropzone.classList.remove("dragover")
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files
            fileInput.dispatchEvent(new Event("change"))
        }
    })
}

async function upload() {
    let file = document.getElementById("fileUpload").files[0]
    if (!file) {
        alert("Choose a file first")
        return
    }

    let form = new FormData()
    form.append("file", file)

    let uploadBtn = document.getElementById("uploadBtn")
    uploadBtn.disabled = true
    uploadBtn.querySelector("span").textContent = "Uploading..."

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

        // Clear welcome message on first upload
        clearWelcome()
        loadDocs()
    } catch (e) {
        alert("Could not connect to server")
        console.error("Upload error:", e)
    } finally {
        uploadBtn.disabled = false
        uploadBtn.querySelector("span").textContent = "Upload PDF"
        document.getElementById("fileUpload").value = ""
        // Reset dropzone text
        const dropzone = document.getElementById("dropzone")
        if (dropzone) {
            dropzone.querySelector(".upload-text").textContent = "Drop PDF here or click to browse"
            dropzone.querySelector(".upload-hint").textContent = "Max 10MB · PDF only"
        }
    }
}

// ===== Typing Indicator =====

function addTypingIndicator() {
    let box = document.getElementById("chatbox")
    let div = document.createElement("div")
    div.className = "typing-indicator"
    div.innerHTML = `<span></span><span></span><span></span>`
    box.appendChild(div)
    box.scrollTop = box.scrollHeight
    return div
}

// ===== Chat =====

function clearWelcome() {
    const welcome = document.querySelector(".welcome-message")
    if (welcome) welcome.remove()
}

async function send() {
    let input = document.getElementById("msg")
    let msg = input.value.trim()

    if (!msg) return

    clearWelcome()
    addMessage(msg, "user")
    input.value = ""

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
        addMessage(data.response, "ai")

        if (data.fallback) {
            let btn = document.createElement("button")
            btn.className = "fallback-btn"
            btn.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="16" x2="12" y2="12"/>
                    <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                Ask General AI
            `

            btn.onclick = async () => {
                btn.style.display = "none"
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
                        btn.style.display = "inline-flex"
                        return
                    }

                    let d = await r.json()
                    addMessage(d.response, "ai")
                    btn.remove()
                } catch (e) {
                    fallbackThinking.remove()
                    addMessage("Could not connect to server", "ai")
                    btn.style.display = "inline-flex"
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

function addMessage(text, type) {
    let box = document.getElementById("chatbox")
    let div = document.createElement("div")
    div.className = "message " + type
    div.innerHTML = marked.parse(text)
    box.appendChild(div)
    box.scrollTop = box.scrollHeight
    return div
}

// ===== Document List =====

async function loadDocs() {
    try {
        let res = await fetch(API + "/documents")
        if (!res.ok) {
            console.error("Failed to load documents")
            return
        }
        let docs = await res.json()
        let div = document.getElementById("docs")
        let emptyState = document.getElementById("emptyState")
        div.innerHTML = ""

        let keys = Object.keys(docs)

        if (keys.length === 0) {
            if (emptyState) emptyState.style.display = "flex"
            return
        }

        if (emptyState) emptyState.style.display = "none"

        for (let id of keys) {
            let d = docs[id]
            let el = document.createElement("div")
            el.className = "docItem"
            el.id = `doc-${id}`

            el.innerHTML = `
                <div class="doc-icon">PDF</div>
                <span class="doc-name" title="${d.name}">${d.name}</span>
                <button class="delete-btn" onclick="delDoc('${id}', this.closest('.docItem'))" title="Delete document">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                </button>
            `
            div.appendChild(el)
        }
    } catch (e) {
        console.error("loadDocs error:", e)
    }
}

// Optimistic UI delete
async function delDoc(id, element) {
    if (element) {
        element.style.opacity = '0.4'
        element.style.pointerEvents = 'none'
        element.style.transform = 'translateX(-8px)'
    }

    try {
        let res = await fetch(API + "/documents/" + id, {
            method: "DELETE"
        })

        if (!res.ok) {
            alert("Failed to delete document")
            if (element) {
                element.style.opacity = '1'
                element.style.pointerEvents = 'all'
                element.style.transform = 'translateX(0)'
            }
            return
        }

        if (element) element.style.display = 'none'
        loadDocs()
    } catch (e) {
        alert("Could not connect to server")
        if (element) {
            element.style.opacity = '1'
            element.style.pointerEvents = 'all'
            element.style.transform = 'translateX(0)'
        }
        console.error("Delete error:", e)
    }
}

// ===== Mobile Sidebar =====

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar")
    let overlay = document.querySelector(".sidebar-overlay")

    if (!overlay) {
        overlay = document.createElement("div")
        overlay.className = "sidebar-overlay"
        overlay.onclick = toggleSidebar
        document.body.appendChild(overlay)
    }

    sidebar.classList.toggle("open")
    overlay.classList.toggle("active")
}

// ===== Init =====

document.addEventListener("DOMContentLoaded", () => {
    setupDropzone()

    let msgInput = document.getElementById("msg")
    if (msgInput) {
        msgInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault()
                send()
            }
        })
    }
})

loadDocs()