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


# ==================================================
# CODE SECURITY ANALYZER
# ==================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    code = data.get("code", "")

    lines = code.split("\n")

    vulnerabilities = []

    score = 100

    critical = 0
    high = 0
    medium = 0
    safe = 0


    weak_passwords = [
        '"123456"',
        "'123456'",
        '"password"',
        "'password'",
        '"admin"',
        "'admin'",
        '"qwerty"',
        "'qwerty'"
    ]


    for number, line in enumerate(lines, start=1):

        text = line.lower()


        if "password =" in text:

            vulnerabilities.append({

                "title": "Hardcoded Password",
                "line": number,
                "severity": "High",

                "explanation":
                "Passwords should not be stored directly in source code.",

                "fix":
                "Use environment variables.",

                "patch":
                'import os\n\npassword = os.getenv("PASSWORD")'

            })

            high += 1
            score -= 20



        if any(value in text for value in weak_passwords):

            vulnerabilities.append({

                "title": "Weak Password",

                "line": number,

                "severity": "Medium",

                "explanation":
                "The password is easy to guess.",

                "fix":
                "Create a strong password.",

                "patch":
                'password = "S3cure@2026"'

            })

            medium += 1
            score -= 10



        if "select" in text:

            vulnerabilities.append({

                "title": "SQL Injection",

                "line": number,

                "severity": "Critical",

                "explanation":
                "SQL queries should not directly use user input.",

                "fix":
                "Use parameterized queries.",

                "patch":
                'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))'

            })

            critical += 1
            score -= 30



        if "eval(" in text:

            vulnerabilities.append({

                "title": "Dangerous eval()",

                "line": number,

                "severity": "High",

                "explanation":
                "eval() can execute unsafe code.",

                "fix":
                "Avoid using eval().",

                "patch":
                "# Remove eval()"

            })

            high += 1
            score -= 20



    if not vulnerabilities:

        vulnerabilities.append({

            "title":
            "No Vulnerabilities Found",

            "line":
            "-",

            "severity":
            "Safe",

            "explanation":
            "No common security issues detected.",

            "patch":
            "No patch needed."

        })

        safe = 1


    score = max(score, 0)


    return jsonify({

        "status": "success",

        "message": "Analysis completed",

        "score": score,

        "critical": critical,

        "high": high,

        "medium": medium,

        "safe": safe,

        "vulnerabilities": vulnerabilities

    })
# ==================================================
# AUTO PATCH GENERATOR
# ==================================================

@app.route("/generate_patch", methods=["POST"])
def generate_patch():

    data = request.get_json()

    code = data.get("code", "")

    fixed_code = code


    replacements = {

        'password = "123456"':
        'import os\n\npassword = os.getenv("PASSWORD")',

        "password = '123456'":
        "import os\n\npassword = os.getenv('PASSWORD')",

        'password = "password"':
        'import os\n\npassword = os.getenv("PASSWORD")',

        "password = 'password'":
        "import os\n\npassword = os.getenv('PASSWORD')",

        'password = "admin"':
        'import os\n\npassword = os.getenv("PASSWORD")',

        "password = 'admin'":
        "import os\n\npassword = os.getenv('PASSWORD')",

        'password = "qwerty"':
        'import os\n\npassword = os.getenv("PASSWORD")',

        "password = 'qwerty'":
        "import os\n\npassword = os.getenv('PASSWORD')"

    }


    for old, new in replacements.items():

        fixed_code = fixed_code.replace(old, new)



    return jsonify({

        "status": "success",

        "fixed_code": fixed_code

    })





# ==================================================
# GITHUB REPOSITORY SCANNER
# ==================================================

@app.route("/scan_github", methods=["POST"])
def scan_github():


    data = request.get_json()

    repo_url = data.get("url")



    if not repo_url:

        return jsonify({

            "status": "error",

            "message": "Repository URL required"

        })



    folder = "temp_repo"



    try:


        # Remove previous cloned repo

        if os.path.exists(folder):

            try:

                shutil.rmtree(folder)

            except Exception:

                pass



        # Clone GitHub repository

        git.Repo.clone_from(

            repo_url,

            folder

        )



        results = []

        files_scanned = 0

        score = 100



        weak_values = [

            '"123456"',
            "'123456'",
            '"password"',
            "'password'",
            '"admin"',
            "'admin'"
        ]



        for root, dirs, files in os.walk(folder):


            for filename in files:


                if filename.endswith(".py"):


                    files_scanned += 1


                    path = os.path.join(

                        root,

                        filename

                    )


                    problems = []



                    with open(

                        path,

                        "r",

                        encoding="utf-8",

                        errors="ignore"

                    ) as file:


                        lines = file.readlines()



                    for line_number, line in enumerate(lines, start=1):


                        text = line.lower()



                        if "password =" in text:


                            problems.append({

                                "issue":
                                "Hardcoded Password",

                                "line":
                                line_number,

                                "severity":
                                "High"

                            })

                            score -= 20




                        if any(value in text for value in weak_values):


                            problems.append({

                                "issue":
                                "Weak Password",

                                "line":
                                line_number,

                                "severity":
                                "Medium"

                            })

                            score -= 10




                        if "eval(" in text:


                            problems.append({

                                "issue":
                                "Dangerous eval()",

                                "line":
                                line_number,

                                "severity":
                                "High"

                            })

                            score -= 20




                    results.append({

                        "file": filename,

                        "issues": problems

                    })



        score = max(score, 0)



        return jsonify({

            "status": "success",

            "repository": repo_url,

            "files_scanned": files_scanned,

            "score": score,

            "results": results

        })


    except Exception as error:


        return jsonify({

            "status": "error",

            "message": str(error)

        })


    finally:

        if os.path.exists(folder):

            try:

                shutil.rmtree(folder)

            except Exception:

                pass


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )