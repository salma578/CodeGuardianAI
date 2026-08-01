from flask import Flask, request, jsonify
from flask_cors import CORS
import git
import os
import shutil
import tempfile


app = Flask(__name__)
CORS(app)



@app.route("/")
def home():
    return "CodeGuardianAI Backend is Running!"



# ======================================================
# CODE ANALYZER
# ======================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json(silent=True) or {}

    code = data.get("code", "")


    vulnerabilities = []

    score = 100

    critical = 0
    high = 0
    medium = 0
    safe = 0



    weak_passwords = [
        "123456",
        "password",
        "admin",
        "qwerty"
    ]



    for line_number, line in enumerate(code.splitlines(), start=1):

        text = line.lower()



        # Hardcoded Password

        if "password =" in text:


            vulnerabilities.append({

                "title": "Hardcoded Password",

                "line": line_number,

                "severity": "High",

                "explanation":
                "Passwords should not be stored directly in source code.",

                "fix":
                "Use environment variables.",

                "patch":
                'import os\npassword = os.getenv("PASSWORD")'

            })


            high += 1

            score -= 20




        # Weak Password

        if "=" in text and any(

            f'"{word}"' in text or f"'{word}'" in text

            for word in weak_passwords

        ):


            vulnerabilities.append({

                "title": "Weak Password",

                "line": line_number,

                "severity": "Medium",

                "explanation":
                "Weak password detected.",

                "fix":
                "Use a strong password.",

                "patch":
                'password = "S3cure@2026"'

            })


            medium += 1

            score -= 10





        # SQL Injection

        if "select" in text:


            vulnerabilities.append({

                "title": "SQL Injection",

                "line": line_number,

                "severity": "Critical",

                "explanation":
                "Possible SQL Injection detected.",

                "fix":
                "Use parameterized queries.",

                "patch":
                'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))'

            })


            critical += 1

            score -= 30





        # Eval

        if "eval(" in text:


            vulnerabilities.append({

                "title": "Dangerous eval()",

                "line": line_number,

                "severity": "High",

                "explanation":
                "eval can execute unsafe code.",

                "fix":
                "Remove eval().",

                "patch":
                "# Remove eval()"

            })


            high += 1

            score -= 20





    if len(vulnerabilities) == 0:


        vulnerabilities.append({

            "title":
            "No Vulnerabilities Found",

            "line":
            "-",

            "severity":
            "Safe",

            "explanation":
            "No security issues detected.",

            "patch":
            "No patch needed."

        })


        safe = 1





    return jsonify({

        "status":
        "success",

        "message":
        "Analysis completed",

        "score":
        max(score,0),

        "critical":
        critical,

        "high":
        high,

        "medium":
        medium,

        "safe":
        safe,

        "vulnerabilities":
        vulnerabilities

    })





# ======================================================
# AUTO PATCH GENERATOR
# ======================================================


@app.route("/generate_patch", methods=["POST"])
def generate_patch():


    data = request.get_json(silent=True) or {}


    code = data.get("code","")



    replacements = {


        'password = "123456"':

        'import os\npassword = os.getenv("PASSWORD")',



        "password = '123456'":

        "import os\npassword = os.getenv('PASSWORD')"

    }




    for old,new in replacements.items():

        code = code.replace(old,new)




    return jsonify({

        "status":
        "success",

        "fixed_code":
        code

    })






# ======================================================
# GITHUB REPOSITORY SCANNER
# ======================================================



@app.route("/scan_github", methods=["POST"])
def scan_github():


    data = request.get_json(silent=True) or {}


    repo_url = data.get("url")



    if not repo_url:


        return jsonify({

            "status":
            "error",

            "message":
            "Repository URL required"

        }),400





    folder = tempfile.mkdtemp(prefix="codeguardian_")



    try:


        git.Repo.clone_from(

            repo_url,

            folder

        )



        results=[]

        files_scanned=0

        score=100



        weak_passwords=[

            "123456",

            "password",

            "admin",

            "qwerty"

        ]




        for root,dirs,files in os.walk(folder):


            dirs[:] = [

                d for d in dirs

                if d not in [

                    ".git",

                    ".venv",

                    "venv",

                    "node_modules",

                    "__pycache__"

                ]

            ]



            if "site-packages" in root:

                continue





            for filename in files:



                if not filename.endswith(".py"):

                    continue




                files_scanned += 1



                file_path=os.path.join(

                    root,

                    filename

                )



                issues=[]



                try:


                    with open(

                        file_path,

                        "r",

                        encoding="utf-8",

                        errors="ignore"

                    ) as f:


                        lines=f.readlines()





                    for line_number,line in enumerate(lines,start=1):


                        text=line.lower()





                        if "password =" in text:


                            issues.append({

                                "issue":
                                "Hardcoded Password",

                                "line":
                                line_number,

                                "severity":
                                "High"

                            })


                            score -=20






                        if "=" in text and any(

                            f'"{word}"' in text or f"'{word}'" in text

                            for word in weak_passwords

                        ):


                            issues.append({

                                "issue":
                                "Weak Password",

                                "line":
                                line_number,

                                "severity":
                                "Medium"

                            })


                            score -=10






                        if "eval(" in text:


                            issues.append({

                                "issue":
                                "Dangerous eval()",

                                "line":
                                line_number,

                                "severity":
                                "High"

                            })


                            score -=20






                        if "select" in text:


                            issues.append({

                                "issue":
                                "SQL Injection",

                                "line":
                                line_number,

                                "severity":
                                "Critical"

                            })


                            score -=30






                    results.append({

                        "file":
                        os.path.relpath(

                            file_path,

                            folder

                        ),

                        "issues":
                        issues

                    })



                except Exception:

                    continue





        return jsonify({

            "status":
            "success",

            "repository":
            repo_url,

            "files_scanned":
            files_scanned,

            "score":
            max(score,0),

            "results":
            results

        })





    except Exception as e:


        return jsonify({

            "status":
            "error",

            "message":
            str(e)

        }),500





    finally:


        if os.path.exists(folder):

            shutil.rmtree(

                folder,

                ignore_errors=True

            )







if __name__=="__main__":


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )