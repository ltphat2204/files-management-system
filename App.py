import tkinter as tk
import Volume
from Shell import Shell
from tkinter import messagebox, scrolledtext

class App():
    def __init__(self, appName = "App", size = "300x300") -> None:
        self.app = tk.Tk()
        self.app.title(appName)
        self.app.geometry(size)
        self.app.resizable(width=False, height=False)

    def _showHeading(self, frame):
        info_text = tk.Text(frame, wrap=tk.WORD, height=12)
        info_text.pack(side="top", fill="x")

        with open("heading_information.txt", "r", encoding="utf-8") as file:
            info_data = file.read()

        info_text.insert(tk.END, info_data)

        info_text.tag_configure("center", justify='center')
        info_text.tag_configure("bold", font=("TkDefaultFont", 14, "bold"))

        info_text.tag_add("center", "1.0", "1.end")
        info_text.tag_add("bold", "1.0", "1.end")

        info_text.config(state=tk.DISABLED)

    def _showAvailableVolumes(self, masterFrame):
        def open_terminal(volume):
            try:
                shell = Shell(Volume.GetVolumeHandler(volume))

                shell_window = tk.Toplevel(self.app)
                shell_window.resizable(width=False, height=False)

                shell_window.title(f"Terminal - {volume}")
                shell_window.geometry("600x400")

                main_frame = tk.Frame(shell_window)
                main_frame.pack(side="top", fill="both", padx=10, pady=10)

                output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=100, height=20)
                output_text.pack(expand=True, fill="both")

                input_label = tk.Label(main_frame, text="Enter Command:")
                input_label.pack(anchor="w")

                input_entry = tk.Entry(main_frame)
                input_entry.pack(fill="x")

                def execute_command(event=None):
                    command = input_entry.get().strip()
                    print(command)
                    if command == 'clear':
                        output_text.delete('1.0', tk.END)
                        input_entry.delete(0, tk.END)
                        return
                    if command:
                        output_text.insert(tk.END, f"\n{shell.prompt}{command}\n")
                        if command.strip() == "help":
                            with open("help.txt", "r", encoding="utf-8") as file:
                                help_data = file.read()
                            output_text.insert(tk.END, f"{help_data}\n")
                            output_text.see(tk.END)
                        else:
                            try:
                                shell.output = ""
                                shell.onecmd(command)
                                if shell.output == "close":
                                    shell_window.destroy()
                                output_text.insert(tk.END, f"{shell.output}\n")
                                output_text.see(tk.END)
                            except Exception as e:
                                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                    input_entry.delete(0, tk.END)

                input_entry.bind("<Return>", execute_command)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        def get_information(volume):
            try:
                volume_info = Volume.GetVolumeInformation(volume)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                return

            info_window = tk.Toplevel(self.app)
            info_window.resizable(width=False, height=False)
            info_window.title("Volume Information")
            info_window.geometry("300x350")

            index = 0
            for key, value in volume_info.items():
                info_label = tk.Label(info_window, text=key + ":", justify="left", font=("TkDefaultFont", 10, "bold"))
                info_label.grid(column=0, row=index, padx=5, pady=5, sticky="w")
                info_label = tk.Label(info_window, text=value, justify="left", font=("TkDefaultFont", 10, "normal"))
                info_label.grid(column=1, row=index, padx=5, pady=5, sticky="w")
                index += 1

        tk.Label(masterFrame, text="Available volumes:", font=("TkDefaultFont", 12, "bold")).pack(side="top", fill="x")

        container = ScrollableFrame(masterFrame)
        container.pack(side="top", fill="both")

        frame = tk.Frame(container.scrollable_frame)
        frame.pack(side="top", fill="both")

        volumes = Volume.GetAllAvailableVolumes()

        for index, volume in enumerate(volumes):
            volume_label = tk.Label(frame, text=volume)
            volume_label.grid(row=index+1, column=0, sticky="w", padx=(5, 10), pady=(0, 5))

            terminal_button = tk.Button(frame, text="Open Terminal", command=lambda v=volume: open_terminal(v))
            terminal_button.grid(row=index+1, column=1, sticky="e", padx=(0, 5), pady=(0, 5))

            info_button = tk.Button(frame, text="Get Information", command=lambda v=volume: get_information(v))
            info_button.grid(row=index+1, column=2, sticky="e", padx=(0, 5), pady=(0, 5))

    
    def Run(self) -> None:
        main_frame = tk.Frame(self.app)
        main_frame.pack(side="top", fill="both", padx=10, pady=10)
        self._showHeading(main_frame)
        self._showAvailableVolumes(main_frame)
        self.app.mainloop()


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Create a canvas widget
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create another frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas)
        
        # Bind the canvas to the scrollbar
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)

        # Bind the event to adjust the scroll region
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)

        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_frame_configure(self, event):
        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta//120), "units")

        