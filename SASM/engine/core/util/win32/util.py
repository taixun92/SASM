# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/core/util/message.py
# Author : Hoon
#
# ====================== Comments ======================
# 

import os

from threading import Thread
from tkinter   import Tk, PhotoImage, Label

from engine.core.const.alias    import INFO, WARNING, ERROR
from engine.core.config.default import WEB_PATH

from win32api import MessageBox
# 윈도우용 메시지 박스 함수
def messagebox( title, message, msg_type=None ):
    EngineSplashImage.destroy()
    if   msg_type == INFO   : MessageBox( 0, message, title, 0  )
    elif msg_type == WARNING: MessageBox( 0, message, title, 48 )
    elif msg_type == ERROR  : MessageBox( 0, message, title, 16 )

# if __name__=='__main__':
#     messagebox( 'hello', 'world', msg_type=ERROR )

class EngineSplashImage:
    loop_active = True

    @classmethod
    def show( cls ):
        def _loop():
            root = Tk()
            root.overrideredirect( True )

            image = PhotoImage( file = os.path.join( WEB_PATH, 'static', 'image', 'login_bg.png' ) )
            label = Label( root, image=image )
            label.pack()

            width  = 261
            height = 450

            x = int( ( root.winfo_screenwidth()  - width  ) / 2 )
            y = int( ( root.winfo_screenheight() - height ) / 2 )

            root.geometry( f'{width}x{height}+{x}+{y}' )

            ###############################################
            # 해당 배너가 항상 다른 창 위에 위치하게 함
            ###############################################
            root.wm_attributes("-topmost", 1)

            root.resizable(False, False)
            root.update_idletasks()

            while cls.loop_active:
                root.update()

                if cls.loop_active == False:
                    root.quit()
                    break
                else:
                    label = Label( root, image=image )
                    label.pack()

        cls.th        = Thread( target=_loop, kwargs=None )
        cls.th.daemon = True
        cls.th.start()
    
    @classmethod
    def destroy(cls):
        cls.loop_active = False
        try   : del cls.th
        except: pass