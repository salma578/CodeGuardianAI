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

def analyze_security(code):

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


        if "password =" in text and "os.getenv" not in text:

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



        if "select" in text and "cursor.execute" not in text:

            vulnerabilities.append({

                "title": "SQL Injection",
                "line": line_number,
                "severity": "Critical",
                "explanation":
                "Possible SQL Injection detected.",
                "fix":
                "Use parameterized queries.",
                "patch":
                "Use parameterized SQL queries."

            })

            critical += 1
            score -= 30



    if not vulnerabilities:

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



    return {

        "score": max(score,0),
        "critical": critical,
        "high": high,
        "medium": medium,
        "safe": safe,
        "vulnerabilities": vulnerabilities

    }





@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json(silent=True) or {}

    code = data.get("code","")


    result = analyze_security(code)


    return jsonify({

        "status":
        "success",

        "message":
        "Analysis completed",

        **result

    })





# ======================================================
# AUTO PATCH
# ======================================================


@app.route("/generate_patch", methods=["POST"])
def generate_patch():

    data = request.get_json(silent=True) or {}

    code = data.get("code", "")


    replacements = {

        'password = "123456"':
        'import os\npassword = os.getenv("PASSWORD")',

        "password = '123456'":
        "import os\npassword = os.getenv('PASSWORD')",

        'password = "password"':
        'import os\npassword = os.getenv("PASSWORD")',

        "password = 'password'":
        "import os\npassword = os.getenv('PASSWORD')",

        'password = "admin"':
        'import os\npassword = os.getenv("PASSWORD")',

        "password = 'admin'":
        "import os\npassword = os.getenv('PASSWORD')",

        'password = "qwerty"':
        'import os\npassword = os.getenv("PASSWORD")',

        "password = 'qwerty'":
        "import os\npassword = os.getenv('PASSWORD')",

        "eval(input())":
        "# Removed unsafe eval()\n    # Use safe input validation instead"

    }


    for old, new in replacements.items():

        code = code.replace(old, new)


    return jsonify({

        "status": "success",

        "fixed_code": code

    })
# ======================================================
# GITHUB SCANNER
# ======================================================


@app.route("/scan_github", methods=["POST"])
def scan_github():


    data = request.get_json(silent=True) or {}

    repo_url = data.get("url")



    if not repo_url:

        return jsonify({

            "status":"error",

            "message":"Repository URL required"

        }),400



    folder = tempfile.mkdtemp(prefix="codeguardian_")



    try:


        git.Repo.clone_from(
            repo_url,
            folder
        )


        results=[]

        files_scanned=0

        total_score=100



        for root, dirs, files in os.walk(folder):


            dirs[:] = [

                d for d in dirs

                if d not in [

                    ".git",
                    ".venv",
                    "venv",
                    "node_modules",
                    "__pycache__",
                    "tests",
                    "test"

                ]

            ]



            if "site-packages" in root:

                continue




            for filename in files:


                if filename == "app.py":

                    continue
                if not filename.endswith(".py"):
                    continue



                files_scanned += 1


                path=os.path.join(
                    root,
                    filename
                )


                try:


                    with open(
                        path,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:

                        code=f.read()



                    analysis=analyze_security(code)


                    if analysis["score"] < total_score:

                        total_score=analysis["score"]




                    issues=[]


                    for item in analysis["vulnerabilities"]:


                        if item["severity"] != "Safe":

                            issues.append({

                                "issue":
                                item["title"],

                                "line":
                                item["line"],

                                "severity":
                                item["severity"]

                            })




                    results.append({

                        "file":
                        os.path.relpath(
                            path,
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
            total_score,

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