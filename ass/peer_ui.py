import tkinter as tk
from tkinter import messagebox
import re
import sys
from threading import Thread

from peer import peer_server,peer_peer

CLIENT_COMMAND = "\n**** Invalid syntax ****\nFormat of client's commands\n1. publish lname fname\n2. fetch fname\n3. clear\n\n"

PUBLISH_PATTERN = r"^publish [a-zA-Z0-9]+\.[a-zA-Z0-9]+ [a-zA-Z0-9]+\.[a-zA-Z0-9]+"
FETCH_PATTERN = r"^fetch\s[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"\\|,.<>\/?]*\.[A-Za-z0-9]+$"
CLEAR_PATTERN = r"^clear$"

class Client_App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Some declarations
        self.username, self.password = None, None
        self.client = None
        self.client_on = None
        self.conn_server = None

        self.mode = False
        self.list_of_ips = None
        self.fname = None

        self.title("File Sharing Application")
        self.minsize(600, 400)

        # Used for manage the current page
        self.current_page_frame = None

        self.current_page_frame = self.main_page()
        self.current_page_frame.pack()
        
        p2p = peer_peer()
        Thread_With_Peer = Thread(target=p2p.Threadlisten, args=())
        Thread_With_Peer.setDaemon(True)
        Thread_With_Peer.start()

    def trigger(self, frame):
        """
        This function used for page redirection

        Parameters: None
        Return: None
        """
        self.current_page_frame.pack_forget()
        self.current_page_frame = frame()
        self.current_page_frame.pack()

    def sign_up_submit(self, username_entry, password_entry):
        """
        This function used for handling register submission.

        Parameters:
        + username_entry (tk.Entry): Entry for username
        + password_entry (tk.Entry): Entry for password
        Return: None
        """
        username = username_entry.get()
        password = password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Lỗi đăng kí", "Vui lòng điền đầy đủ thông tin.")
            return

        # Send username and password to server step
        self.client = peer_server()
        conn = self.client.connect("192.168.137.2",3000)
        message = self.client.regist_message(conn, username, password)
        self.client.stop(conn)
        del self.client

        if message != 'Regist success':
            messagebox.showerror("Lỗi đăng kí", message)
        else:
            messagebox.showinfo("Đăng kí thành công", "Đăng kí thành công! Vui lòng đăng nhập để sử dụng dịch vụ.")

            self.current_page_frame.pack_forget()
            self.current_page_frame = self.sign_in()
            self.current_page_frame.pack()

    
    def sign_up(self):
        """
        This function used for create a sign up frame

        Parameters: None
        Return:
        sign_up_frame (tk.Frame): The sign up frame
        """
        sign_up_frame = tk.Frame(borderwidth = 70)

        sign_up_label = tk.Label(sign_up_frame, text="SIGN UP", font=("San Serif", 24, "bold"), borderwidth = 10)
        sign_up_label.grid(row = 0, column = 0, columnspan = 10)

        sign_up_username_label = tk.Label(sign_up_frame, text="Username", font=("San Serif", 13, "bold"))
        sign_up_username_label.grid(row=1, column=0, sticky="we", padx = 10, pady=10)
        sign_up_username_entry = tk.Entry(sign_up_frame, width = 50, font=("San Serif", 13))
        sign_up_username_entry.grid(row=1, column=1, columnspan = 9, sticky = "we", padx = 10, pady = 10, ipadx=2, ipady = 2)
        sign_up_username_entry.bind('<Return>', lambda event: self.submit(sign_up_username_entry, sign_up_password_entry))

        sign_up_password_label = tk.Label(sign_up_frame, text="Password", font=("San Serif", 13, "bold"))
        sign_up_password_label.grid(row=2, column=0, sticky="we", padx = 10, pady=10)
        sign_up_password_entry = tk.Entry(sign_up_frame, show="*", width = 50, font=("San Serif", 13))
        sign_up_password_entry.grid(row=2, column=1, columnspan= 9, sticky = "we", padx = 10, pady = 10, ipadx=2, ipady = 2)
        sign_up_password_entry.bind('<Return>', lambda event: self.sign_up_submit(sign_up_username_entry, sign_up_password_entry))

        sign_up_button = tk.Button(sign_up_frame, text="Sign Up", font=("San Serif", 13), command = lambda: self.sign_up_submit(sign_up_username_entry, sign_up_password_entry))
        sign_up_button.grid(row = 3, column = 1)
        return_button = tk.Button(sign_up_frame, text = "Main Page", font=("San Serif", 13), command = lambda: self.trigger(self.main_page))
        return_button.grid(row = 3, column = 6)

        return sign_up_frame

    def check_login(self, username_entry, password_entry):
        """
        Used for authentication

        Parameters:
        + usename_entry (tk.Entry):
        + password_entry (tk.Entry):

        """
        username = username_entry.get()
        password = password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Lỗi đăng nhập", "Vui lòng điền đầy đủ thông tin.")
            return
        
        self.client = peer_server()
        conn = self.client.connect("192.168.137.2",3000)
        self.client.assign_server_conn(conn)
        message = self.client.login_message(conn, username, password)

        if not message == 'Login success':
            self.client.stop(conn)
            del self.client

        if message != 'Login success':
            messagebox.showerror("Lỗi đăng nhập", message)
        else:
            self.username = username
            self.password = password
            self.client_on = True
            self.conn_server = conn
            messagebox.showinfo("Đăng nhập thành công", "Chào mừng, " + username + "!")

            self.current_page_frame.pack_forget()
            self.current_page_frame = self.terminal()
            self.current_page_frame.pack()

    def sign_in(self):
        sign_in_frame = tk.Frame(borderwidth = 70)

        sign_in_label = tk.Label(sign_in_frame, text="SIGN IN", font=("San Serif", 24, "bold"), borderwidth = 10)
        sign_in_label.grid(row = 0, column = 0, columnspan = 10)

        sign_in_username_label = tk.Label(sign_in_frame, text="Username", font=("San Serif", 13, "bold"))
        sign_in_username_label.grid(row=1, column=0, sticky="we", padx = 10, pady=10)
        sign_in_username_entry = tk.Entry(sign_in_frame, width = 50, font=("San Serif", 13))
        sign_in_username_entry.grid(row=1, column=1, columnspan = 9, sticky = "we", padx = 10, pady = 10, ipadx=2, ipady = 2)
        sign_in_username_entry.bind('<Return>', lambda event: self.check_login(sign_in_username_entry, sign_in_password_entry))

        sign_in_password_label = tk.Label(sign_in_frame, text="Password", font=("San Serif", 13, "bold"))
        sign_in_password_label.grid(row=2, column=0, sticky="we", padx = 10, pady=10)
        sign_in_password_entry = tk.Entry(sign_in_frame, show="*", width = 50, font=("San Serif", 13))
        sign_in_password_entry.grid(row=2, column=1, columnspan= 9, sticky = "we", padx = 10, pady = 10, ipadx=2, ipady = 2)
        sign_in_password_entry.bind('<Return>', lambda event: self.check_login(sign_in_username_entry, sign_in_password_entry))

        sign_in_button = tk.Button(sign_in_frame, text="Sign In", font=("San Serif", 13), command = lambda: self.check_login(sign_in_username_entry, sign_in_password_entry))
        sign_in_button.grid(row = 3, column = 1)
        return_button = tk.Button(sign_in_frame, text = "Main Page", font=("San Serif", 13), command = lambda: self.trigger(self.main_page))
        return_button.grid(row = 3, column = 6)

        return sign_in_frame

    def main_page(self):
        main_page_frame = tk.Frame(borderwidth = 50)

        main_page_label = tk.Label(main_page_frame, text="FILE SHARING APPLICATION", font=("San Serif", 30, "bold"), borderwidth = 50)
        main_page_label.grid(row = 0, column = 0)

        b1 = tk.Button(main_page_frame, text = "Sign In", font=("San Serif", 14) , command = lambda: self.trigger(self.sign_in))
        b1.grid(row = 1, column = 0, pady = 5)

        
        b2 = tk.Button(main_page_frame, text = "Sign Up", font=("San Serif", 14), command = lambda: self.trigger(self.sign_up))
        b2.grid(row = 3, column = 0, pady = 5)

        return main_page_frame

    def command_processing(self, command):
        """
        Return True when the command is in the correct format
        """
        if re.search(FETCH_PATTERN, command) or re.search(PUBLISH_PATTERN, command) \
            or re.search(CLEAR_PATTERN, command):
            return True
        return False

    def get_response(self, command):
        """
        Use for get response for each command and show it for user

        Return:
        response (String): The result when execute the command
        """
        message = None
        if command == "clear":
            return "clear"
        if re.search(PUBLISH_PATTERN, command):
            _, lname, fname = command.split(" ")
            message = self.client.publish(self.conn_server, lname, fname)
            if message == 'No File':
                return (f'There is no file named: {lname} in your local file system!')
            else:
                return fname
        else:
            _, fname = command.split(" ")
            message = self.client.fetch(self.conn_server, fname)
            return message
            # if message == "NO_AVAILABLE_HOST":
            #     return "Không có peer nào có file hoặc đang sẵn sàng."
            # else:
            #     return [message, fname]

            
    def add_files(self, fname, list_files):
        list_files.config(state = tk.NORMAL)
        list_files.delete(0.1, tk.END)
        list_files.insert(tk.END, "         My Repository      \n\n")
        list_fnames = self.client.get_fname()
        for fname in list_fnames:
            list_files.insert(tk.END, f"* {fname}\n")
        list_files.config(state = tk.DISABLED)

    # Trigger for excute command
    def execute_command(self, input_field, output_field, list_files):
        """
        Used
        """
        command = input_field.get()
        input_field.delete(0, tk.END)
        output_field.config(state=tk.NORMAL)
        if self.mode:
            if not re.search(r"^[1-9]+[0-9]*$", command):
                output_field.insert(tk.END, "\nVui lòng nhập đúng định dạng\n\n", "color")
                output_field.see(tk.END)
            elif int(command) > len(self.list_of_ips):
                output_field.insert(tk.END, f"\nVui lòng chọn số trong khoảng từ 1 đến {len(self.list_of_ips)}\n\n", "color")
                output_field.see(tk.END)
            else:
                output_field.insert(tk.END, f"\nNgười dùng chọn peer số {command}\n", "color")
                output_field.see(tk.END)
                ip = self.list_of_ips[int(command)-1]
                message = self.client.download(self.fname, ip)
                if message == 'DENIED':
                    output_field.insert(tk.END, f"\nLỗi nhận file. Vui lòng thử lại.\n\n", "color")
                    output_field.see(tk.END)
                else:
                    self.add_files(self.fname, list_files)
                    output_field.insert(tk.END, f"\nĐã nhận file thành công!\n\nKích thước {self.client.file_size}B\n\nThời gian {self.client.retrieve_time}s\n\nTốc độ {self.client.speed}B/s", "color")
                    output_field.see(tk.END)   
                
            self.mode = False
        else:
            output_field.insert(tk.END, f"{self.username}$ " + command + "\n", "color")

            if not self.command_processing(command):
                output_field.insert(tk.END, CLIENT_COMMAND, "color")
                output_field.see(tk.END)
            else:
                result = self.get_response(command)
                if command == "clear":
                    output_field.delete(0.1, tk.END)
                    output_field.insert(tk.END, 
                        "Terminal [Version 1.0.0]\nCopyright (C) phuchuynh. All right reserved.\n\n", "color")
                elif command.split(" ")[0] == "publish":
                    if result == "File đã tồn tại!":
                        output_field.insert(tk.END, f"\n{result}\n\n", "color")
                        output_field.see(tk.END)
                    else:
                        output_field.insert(tk.END, f"\nUpload file thành công!\n\n", "color")
                        output_field.see(tk.END)
                        self.add_files(result, list_files)
                else:
                    if result == "Không có peer nào có file hoặc đang sẵn sàng.":
                        output_field.insert(tk.END, f"\n{result}\n\n", "color")
                        output_field.see(tk.END)
                    else:
                        output_field.insert(tk.END, f"\nDanh sách các peer:\n", "color")
                        output_field.see(tk.END)
                        print(result)
                        input_command = command.split()
                        self.fname = input_command[1]
                        self.list_of_ips = result
                        for i in range(0, len(self.list_of_ips)):
                            output_field.insert(tk.END, f"{i+1}. {self.list_of_ips[i]['ipAdress']}\n", "color")
                            output_field.see(tk.END)
                        output_field.insert(tk.END, f"\nHãy chọn peer bạn mong muốn fetch!\n", "color")
                        output_field.see(tk.END)
                        self.mode = True

        output_field.config(state=tk.DISABLED)

    def log_out(self):
        self.client_on = False
        self.client.stop(self.conn_server)
        self.trigger(self.main_page)

    def terminal(self):
        terminal_frame = tk.Frame()

        header = tk.Label(terminal_frame, text = f"Hello, {self.username}", font=("San Serif", 11, "bold"))
        header.grid(row = 0, column = 0, padx = 5, pady = 5)

        log_out_button = tk.Button(terminal_frame, text = "Log Out", command=self.log_out)
        log_out_button.grid(row = 0, column = 89, padx = 5, pady = 5)
        

        terminal_output = tk.Text(terminal_frame, background = "black")
        terminal_output.tag_configure("color", foreground="white")
        terminal_output.insert(tk.END, "Terminal [Version 1.0.0]\nCopyright (C) phuchuynh. All right reserved.\n\n", "color")
        terminal_output.config(state = tk.DISABLED)
        terminal_output.grid(row = 1, column = 0, columnspan = 70, padx = 5, pady = 5)

        list_files = tk.Text(terminal_frame, background = "white", width = 30)
        list_files.grid(row = 1, column = 70, columnspan = 20, padx = 5, pady = 5)
        list_files.insert(tk.END, "         My Repository      \n\n")
        list_of_files = self.client.get_fname()
        for i in list_of_files:
            list_files.insert(tk.END, f"* {i}\n")
        list_files.config(state = tk.DISABLED)

        input_header = tk.Label(terminal_frame, text = ">>>")
        input_header.grid(row = 2, column = 0, sticky="e")

        input_field = tk.Entry(terminal_frame)
        input_field.grid(row = 2, column = 1, columnspan = 89, sticky="we", padx = 5, pady = 10)

        input_field.bind('<Return>', lambda event: self.execute_command(input_field, terminal_output, list_files))
        
        return terminal_frame
    
    def close(self,conn):
        if self.client_on:
            self.client.stop(conn)
        self.destroy()

def main():
    app = Client_App()
    app.protocol("WM_DELETE_WINDOW", lambda: app.close(app.conn_server))
    app.mainloop()

if __name__ == "__main__":
    
    main()