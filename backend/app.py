from flask import Flask, request, jsonify
from flask_cors import CORS

import git
import os
import shutil


app = Flask(__name__)

CORS(app)



@app.route("/")
def home():

    return "CodeGuardianAI Backend is Running!"





# =====================================
# CODE ANALYSIS API
# =====================================

@app.route("/analyze", methods=["POST"])
def analyze():


    data = request.get_json()

    code = data.get("code","")

    lines = code.split("\n")


    vulnerabilities = []


    score = 100

    critical = 0
    high = 0
    medium = 0
    safe = 0




    # Hardcoded Password

    for index,line in enumerate(lines):


        if "password =" in line.lower():


            vulnerabilities.append({

                "title":"Hardcoded Password",

                "line":index+1,

                "severity":"High",

                "explanation":
                "Passwords should never be stored in source code.",

                "fix":
                "Store passwords in environment variables.",

                "ai_recommendation":
                "This vulnerability can expose user credentials. Attackers can extract passwords from source code. Environment variables protect sensitive information.",

                "patch":
                'import os\n\npassword = os.getenv("PASSWORD")'

            })


            high += 1
            score -= 20

            break





    # Weak Password


    weak_passwords=[
        "123456",
        "password",
        "admin",
        "qwerty"
    ]



    for index,line in enumerate(lines):


        for pwd in weak_passwords:


            if pwd in line.lower():


                vulnerabilities.append({

                    "title":"Weak Password",

                    "line":index+1,

                    "severity":"Medium",

                    "explanation":
                    "The password is easy to guess.",

                    "fix":
                    "Use a strong password.",

                    "ai_recommendation":
                    "Weak passwords can be cracked using brute force attacks. Use long passwords with uppercase, lowercase, numbers and symbols.",

                    "patch":
                    'password = "S3cure@2026"'

                })


                medium += 1

                score -= 10

                break






    # SQL Injection


    for index,line in enumerate(lines):


        if "select" in line.lower():


            vulnerabilities.append({

                "title":"SQL Injection",

                "line":index+1,

                "severity":"Critical",

                "explanation":
                "SQL query is created directly from user input.",

                "fix":
                "Use parameterized queries instead of string concatenation.",

                "ai_recommendation":
                "Attackers can manipulate SQL queries and access unauthorized database information.",

                "patch":
                'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))'

            })


            critical += 1

            score -= 30

            break





    # eval


    for index,line in enumerate(lines):


        if "eval(" in line:


            vulnerabilities.append({

                "title":"Dangerous eval()",

                "line":index+1,

                "severity":"High",

                "explanation":
                "eval() can execute dangerous code.",

                "fix":
                "Avoid using eval().",

                "ai_recommendation":
                "eval() may allow attackers to execute malicious commands.",

                "patch":
                "# Remove eval() and validate input"

            })


            high += 1

            score -=20

            break





    if len(vulnerabilities)==0:


        vulnerabilities.append({

            "title":"No Vulnerabilities Found",

            "line":"-",

            "severity":"Safe",

            "explanation":
            "No common security issues detected.",

            "fix":
            "No action required.",

            "ai_recommendation":
            "Your code passed security checks.",

            "patch":
            "No patch needed."

        })


        safe=1




    if score < 0:

        score=0




    return jsonify({

        "status":"success",

        "message":"Analysis completed",

        "score":score,

        "critical":critical,

        "high":high,

        "medium":medium,

        "safe":safe,

        "vulnerabilities":vulnerabilities

    })







# =====================================
# AUTO PATCH GENERATOR
# =====================================


@app.route("/generate_patch",methods=["POST"])
def generate_patch():


    data=request.get_json()


    code=data.get("code","")


    fixed_code=code



    fixed_code=fixed_code.replace(

        'password = "123456"',

        'import os\n\npassword = os.getenv("PASSWORD")'

    )



    fixed_code=fixed_code.replace(

        "password = '123456'",

        "import os\n\npassword = os.getenv('PASSWORD')"

    )




    for pwd in [

        "123456",
        "password",
        "admin",
        "qwerty"

    ]:


        fixed_code=fixed_code.replace(

            f'"{pwd}"',

            '"S3cure@2026"'

        )


        fixed_code=fixed_code.replace(

            f"'{pwd}'",

            "'S3cure@2026'"

        )




    return jsonify({

        "status":"success",

        "fixed_code":fixed_code

    })







# =====================================
# GITHUB REPOSITORY SCANNER
# =====================================


@app.route("/scan_github",methods=["POST"])
def scan_github():


    data=request.get_json()


    repo_url=data.get("repo_url")



    if not repo_url:


        return jsonify({

            "status":"error",

            "message":"Repository URL required"

        })




    folder="temp_repo"



    if os.path.exists(folder):

        shutil.rmtree(folder)




    try:


        git.Repo.clone_from(

            repo_url,

            folder

        )



        combined_code=""



        for root,dirs,files in os.walk(folder):


            for file in files:


                if file.endswith(".py"):


                    path=os.path.join(

                        root,

                        file

                    )


                    with open(

                        path,

                        "r",

                        encoding="utf-8",

                        errors="ignore"

                    ) as f:


                        combined_code += "\n\n" + f.read()




        return jsonify({

            "status":"success",

            "message":
            "Repository scanned successfully",

            "code":
            combined_code

        })




    except Exception as e:


        return jsonify({

            "status":"error",

            "message":str(e)

        })






if __name__=="__main__":

    app.run(debug=True)