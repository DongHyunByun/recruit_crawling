import os
import win32com.client as win32
import win32gui

# 함수
def hwp2pdf(BASE_DIR, SAVE_DIR):
    os.mkdir(SAVE_DIR)  # 폴더생성(미리 생성하는 경우는 삭제해도 됌)
    hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")  # hwp 창열기
    hwnd = win32gui.FindWindow(None, 'Noname 1 - HWP')
    hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')  # 보안모듈 삭제
    a = [os.path.join(file) for file in os.listdir(BASE_DIR) if file.endswith('hwp')]  # 파일경로 지정
    for i in a:  # pdf변환
        hwp.Open(os.path.join(BASE_DIR, i))
        hwp.SaveAs(SAVE_DIR + i[:-4] + ".pdf", "PDF")

hwp2pdf("20220725","hwp2pdf")