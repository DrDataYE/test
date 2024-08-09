import subprocess
import os
import argparse
import random
import string
import time
from rich.console import Console
from rich.progress import track

console = Console()

def run_command(command, cwd=None):
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Error running command:[/red] {command}\n{result.stderr}")
    else:
        console.print(result.stdout)
    return result.returncode

def create_random_file(repo_path):
    filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '.txt'
    filepath = os.path.join(repo_path, filename)
    with open(filepath, 'w') as f:
        f.write(''.join(random.choices(string.ascii_lowercase + string.digits, k=100)))
    console.print(f"[green]Created file:[/green] {filename}")
    return filename

def main(args):
    # إعداد URL المستودع البعيد مع التوكن
    remote_with_token = args.remote_url.replace("https://", f"https://{args.username}:{args.token}@")

    # الانتقال إلى مسار المشروع
    os.chdir(args.repo_path)

    # تهيئة المستودع إذا لم يكن مهيأً
    if not os.path.exists(os.path.join(args.repo_path, ".git")):
        run_command("git init")

    # التحقق من وجود remote مسبقًا
    result = subprocess.run("git remote", shell=True, capture_output=True, text=True)
    if 'origin' in result.stdout:
        run_command("git remote remove origin")

    # إضافة المستودع البعيد
    run_command(f"git remote add origin {remote_with_token}")

    # التأكد من وجود الفرع الرئيسي أو التبديل إليه
    result = subprocess.run("git branch", shell=True, capture_output=True, text=True)
    if 'main' not in result.stdout:
        run_command("git checkout -b main")
    else:
        run_command("git checkout main")

    # دمج التغييرات البعيدة إذا كانت موجودة مع تحديد طريقة الدمج
    run_command("git pull origin main --allow-unrelated-histories --rebase=false")

    # حلقة لإنشاء ملفات عشوائية ورفع التحديثات إلى GitHub
    try:
        while True:
            # إنشاء ملف عشوائي
            create_random_file(args.repo_path)

            # إضافة جميع الملفات إلى المستودع
            run_command("git add .")

            # عمل الالتزام
            run_command('git commit -m "Auto-commit: adding random file"')

            # رفع المشروع إلى GitHub
            run_command("git push -u origin main")

            # تأخير لمدة 10 ثوانٍ قبل التحديث التالي
            # time.sleep(1)
    except KeyboardInterrupt:
        console.print("[red]Process interrupted by user.[/red]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="رفع مشروع إلى GitHub باستخدام بايثون")
    parser.add_argument("--repo_path", default=".", help="مسار المشروع المحلي")
    parser.add_argument("--remote_url", default="https://github.com/DrDataYE/test.git", help="رابط المستودع البعيد")
    parser.add_argument("--token", default="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", help="التوكن الخاص بـ GitHub")
    parser.add_argument("--username", default="DrDataYE", help="اسم المستخدم على GitHub")

    args = parser.parse_args()

    for step in track(["Running Commands"], description="Processing..."):
        main(args)

