import jsPDF from "jspdf";
import { useState } from "react";
import "./App.css";


function App() {


const [code,setCode]=useState("");
const [fileName,setFileName]=useState("");

const [result,setResult]=useState(null);
const [fixedCode,setFixedCode]=useState("");

const [githubUrl,setGithubUrl]=useState("");
const [githubResult,setGithubResult]=useState(null);

const [loading,setLoading]=useState(false);
const [githubLoading,setGithubLoading]=useState(false);




// ================= FILE UPLOAD =================


const handleFileUpload=(event)=>{


const file=event.target.files[0];


if(!file)
return;



if(!file.name.endsWith(".py")){

alert("Please upload only Python files");
return;

}



setFileName(file.name);



const reader=new FileReader();



reader.onload=(e)=>{

setCode(e.target.result);

};



reader.readAsText(file);



};






// ================= ANALYZE CODE =================



const analyzeCode=async()=>{


if(!code){

alert("Please upload or paste Python code");

return;

}



setLoading(true);



try{


const response = await fetch(
  "https://codeguardianai.onrender.com/analyze",
  {

method:"POST",

headers:{

"Content-Type":"application/json"

},


body:JSON.stringify({

code:code

})


}

);



const data=await response.json();



setResult(data);



}

catch(error){

alert("Backend is not running");

}



finally{

setLoading(false);

}



};






// ================= AUTO PATCH =================



const generatePatch=async()=>{


try{


const response = await fetch(
  "https://codeguardianai.onrender.com/generate_patch",
  {
method:"POST",

headers:{

"Content-Type":"application/json"

},


body:JSON.stringify({

code:code

})


}

);



const data=await response.json();



setFixedCode(data.fixed_code);



}

catch(error){

alert("Patch generation failed");

}



};








// ================= GITHUB SCANNER =================



const scanGithub=async()=>{


if(!githubUrl){

alert("Enter GitHub URL");

return;

}



setGithubLoading(true);



try{


const response = await fetch(
  "https://codeguardianai.onrender.com/scan_github",
  {
method:"POST",

headers:{

"Content-Type":"application/json"

},


body:JSON.stringify({

url:githubUrl

})


}

);



const data=await response.json();



if(data.status==="error"){

alert(data.message);

}

else{

setGithubResult(data);

}



}


catch(error){

alert("GitHub scan failed");

}



finally{

setGithubLoading(false);

}



};








// ================= DOWNLOAD FIXED FILE =================



const downloadFixedCode=()=>{


const blob=new Blob(

[fixedCode],

{

type:"text/plain"

}

);



const url=URL.createObjectURL(blob);



const link=document.createElement("a");


link.href=url;


link.download="secure_fixed_code.py";


link.click();



};








// ================= PDF REPORT =================



const downloadReport=()=>{


if(!result){

alert("Analyze code first");

return;

}



const doc=new jsPDF();



doc.text(

"CodeGuardianAI Security Report",

20,

20

);



doc.text(

`Security Score : ${result.score}/100`,

20,

40

);



doc.text(

`Critical : ${result.critical}`,

20,

50

);



doc.text(

`High : ${result.high}`,

20,

60

);



doc.text(

`Medium : ${result.medium}`,

20,

70

);



let y=90;



result.vulnerabilities.forEach((v,index)=>{


doc.text(

`${index+1}. ${v.title} - ${v.severity}`,

20,

y

);


y+=10;


});



doc.save(

"CodeGuardianAI_Report.pdf"

);



};









return (

<div className="container">



<h1>
CodeGuardianAI
</h1>


<h2>
AI Powered Code Security Scanner
</h2>





<div className="upload-box">


<h3>
Upload Python File
</h3>


<input

type="file"

accept=".py"

onChange={handleFileUpload}

/>



{

fileName &&

<p>

Selected File:

<b>
{fileName}
</b>

</p>

}



</div>





<textarea

rows="12"

placeholder="Paste your Python code..."

value={code}

onChange={(e)=>setCode(e.target.value)}

/>





<button onClick={analyzeCode}>

{

loading ?

"Analyzing..." :

"Analyze File"

}

</button>







<hr/>





{

result &&


<div className="card">


<button onClick={downloadReport}>

Download PDF Report

</button>



<button onClick={generatePatch}>

Generate Auto Patch

</button>





<h2>
Security Score
</h2>


<h1>
{result.score}/100
</h1>



<p>
Critical : {result.critical}
</p>


<p>
High : {result.high}
</p>


<p>
Medium : {result.medium}
</p>


<p>
Safe : {result.safe}
</p>





<h2>
Vulnerabilities
</h2>



{

result.vulnerabilities.map(

(v,index)=>(


<div className="card" key={index}>


<h3>
{v.title}
</h3>


<p>
Line : {v.line}
</p>


<p>
Severity : {v.severity}
</p>


<p>
{v.explanation}
</p>


<pre>
{v.patch}
</pre>



</div>


)

)

}



</div>

}







{

fixedCode &&


<div className="card">


<h2>
Before vs After
</h2>



<h3>
Original Code
</h3>


<pre>

{code}

</pre>





<h3>
Secure Code
</h3>


<pre>

{fixedCode}

</pre>




<button onClick={downloadFixedCode}>

Download Fixed Python File

</button>



</div>


}









<hr/>






<h2>
GitHub Repository Scanner
</h2>



<input

type="text"

placeholder="Enter GitHub Repository URL"

value={githubUrl}

onChange={(e)=>setGithubUrl(e.target.value)}

/>




<button onClick={scanGithub}>

{

githubLoading ?

"Scanning..." :

"Scan Repository"

}

</button>






{

githubResult &&


<div className="card">


<h2>
GitHub Scan Result
</h2>



<p>

Files Scanned :

{githubResult.files_scanned}

</p>





{

githubResult.results.map(

(item,index)=>(


<div key={index}>


<h3>
{item.file}
</h3>



{

item.issues.length > 0 ?

item.issues.map(

(issue,i)=>(


<p key={i}>

{issue.issue}

-

{issue.severity}

-

Line {issue.line}

</p>


)

)

:

<p>
No vulnerabilities found
</p>


}



</div>


)

)

}



</div>


}





</div>


);


}


export default App;