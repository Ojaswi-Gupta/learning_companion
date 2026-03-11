
const API = "http://localhost:8000"
console.log("SCRIPT LOADED")
async function upload(){

let file = document.getElementById("fileUpload").files[0]

if(!file){
alert("Choose a file")
return
}

let form = new FormData()

form.append("file", file)

await fetch(API + "/upload",{
method:"POST",
body:form
})

loadDocs()
}



async function send(){

let input=document.getElementById("msg")
let msg=input.value.trim()

if(!msg) return

addMessage(msg,"user")

input.value=""

let thinking=addMessage("Thinking...","ai")

let res=await fetch(API+"/chat?query="+encodeURIComponent(msg),{
method:"POST"
})

let data=await res.json()

console.log("API RESPONSE:",data)

thinking.remove()

let aiDiv=addMessage(data.response,"ai")

if(data.fallback){

let btn=document.createElement("button")

btn.innerText="Ask General AI"

btn.style.marginTop="10px"

btn.onclick=async()=>{

btn.innerText="Thinking..."

let r=await fetch(API+"/general?query="+encodeURIComponent(msg),{
method:"POST"
})

let d=await r.json()

addMessage(d.response,"ai")

btn.remove()

}

document.getElementById("chatbox").appendChild(btn)

}

}



function addMessage(text,type){

let box=document.getElementById("chatbox")

let div=document.createElement("div")

div.className="message "+type

div.innerHTML=marked.parse(text)

box.appendChild(div)

box.scrollTop=box.scrollHeight

return div

}



async function loadDocs(){

let res=await fetch(API+"/documents")

let docs=await res.json()

let div=document.getElementById("docs")

div.innerHTML=""

for(let id in docs){

let d=docs[id]

let el=document.createElement("div")

el.className="docItem"

el.innerHTML=`
<span>${d.name}</span>
<button onclick="delDoc('${id}')">Delete</button>
`

div.appendChild(el)

}

}



async function delDoc(id){

await fetch(API+"/documents/"+id,{
method:"DELETE"
})

loadDocs()

}



loadDocs()