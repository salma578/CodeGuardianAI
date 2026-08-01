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




// Upload Python File

const handleFileUpload=(event)=>{

const file=event.target.files[0];

if(!file) return;


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







// Analyze Code

const analyzeCode=async()=>{


try{


const response=await fetch(
"http://127.0.0.1:5000/analyze",
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


};








// Generate Patch


const generatePatch=async()=>{


try{


const response=await fetch(
"http://127.0.0.1:5000/generate_patch",
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










// GitHub Scanner


const scanGithub=async()=>{


try{


const response=await fetch(
"http://127.0.0.1:5000/scan_github",
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


setGithubResult(data);


}

catch(error){

alert("GitHub scan failed");

}


};










// Download Fixed Code


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











// PDF Report


const downloadReport=()=>{


const doc=new jsPDF();


doc.text(
"CodeGuardianAI Security Report",
20,
20
);


doc.text(
`Security Score: ${result.score}/100`,
20,
40
);


doc.text(
`Critical: ${result.critical}`,
20,
50
);


doc.text(
`High: ${result.high}`,
20,
60
);


doc.text(
`Medium: ${result.medium}`,
20,
70
);


doc.save(
"CodeGuardianAI_Report.pdf"
);


};









return (

<div className="container">


<h1>
CodeGuardianAI
</h1>





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
<b>{fileName}</b>
</p>

}



</div>






<textarea

rows="12"

placeholder="Paste your source code here..."

value={code}

onChange={(e)=>setCode(e.target.value)}

/>





<button onClick={analyzeCode}>

Analyze File

</button>









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

Scan Repository

</button>









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
Vulnerability Details
</h2>




{

result.vulnerabilities &&

result.vulnerabilities.map((v,index)=>(


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


))


}







{

fixedCode &&

<div className="card">


<h2>
Before vs After Comparison
</h2>



<h3>
Original Code
</h3>


<pre>
{code}
</pre>




<h3>
Secure Fixed Code
</h3>


<pre>
{fixedCode}
</pre>




<button onClick={downloadFixedCode}>

Download Fixed Python File

</button>



</div>


}




</div>


}









{

githubResult &&

<div className="card">


<h2>
GitHub Scan Result
</h2>



<p>
Repository:
{githubResult.repository || githubUrl}
</p>



<p>
Files Scanned:
{githubResult.files_scanned}
</p>





{

githubResult.results &&

githubResult.results.map((item,index)=>(


<div key={index}>


<h3>
{item.file}
</h3>



{

item.issues && item.issues.length>0 ?


item.issues.map((issue,i)=>(


<div key={i}>


<p>
Issue: {issue.issue}
</p>


<p>
Line: {issue.line}
</p>


<p>
Severity: {issue.severity}
</p>


</div>


))


:


<p>
No vulnerabilities found
</p>


}



</div>


))


}



</div>


}






</div>

);


}


export default App;