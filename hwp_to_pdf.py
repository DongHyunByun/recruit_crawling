import os
import win32com.client as win32
import win32gui

# 함수
def hwp2pdf(BASE_DIR):
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")  # hwp 창열기
    win32gui.FindWindow(None, 'Noname 1 - HWP')
    hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')  # 보안모듈 삭제

    files = [os.path.join(file) for file in os.listdir(BASE_DIR) if file.endswith('hwp')]  # 파일경로 지정
    for file_name in files:
        hwp.Open(os.path.join(BASE_DIR, file_name))
        pdf_file_name = file_name[:-4]+".pdf"
        hwp.SaveAs(os.path.join(BASE_DIR, pdf_file_name), "PDF")

if __name__ == "__main__":
    hwp2pdf("20220811")