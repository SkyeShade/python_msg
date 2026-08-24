import tkinter as tk

import database


def create_window():
    root = tk.Tk()

    root.title("Very Serious Discord Competitor")
    root.geometry("740x700")

    history_container = tk.LabelFrame(
        root,
        text="Chat History",
        padx=10,
        pady=10
    )
    history_container.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=(10, 5)
    )

    history_canvas = tk.Canvas(
        history_container,
        yscrollincrement=8
    )
    history_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    def on_mousewheel(event):
        history_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    history_canvas.bind_all("<MouseWheel>", on_mousewheel)

    scrollbar = tk.Scrollbar(
        history_container,
        orient="vertical",
        command=history_canvas.yview
    )
    scrollbar.pack(
        side="right",
        fill="y"
    )

    history_canvas.configure(
        yscrollcommand=scrollbar.set
    )

    history_frame = tk.Frame(history_canvas)

    history_canvas.create_window(
        (0, 0),
        window=history_frame,
        anchor="nw"
    )

    history_frame.bind(
        "<Configure>",
        lambda event: history_canvas.configure(
            scrollregion=history_canvas.bbox("all")
        )
    )

    post_frame = tk.LabelFrame(
        root,
        text="New Message",
        padx=10,
        pady=10
    )
    post_frame.pack(
        fill="x",
        padx=10,
        pady=(5, 10)
    )

    load_messages(history_frame)
    create_post_area(post_frame, history_frame)

    return root


def load_messages(history_frame):
    for widget in history_frame.winfo_children():
        widget.destroy()

    messages = database.get_messages()

    for row in messages:
        message_id, title, message, timestamp, last_updated = row

        message_frame = tk.Frame(
            history_frame,
            borderwidth=1,
            relief="solid"
        )
        message_frame.pack(
            fill="x",
            pady=5
        )

        title_entry = tk.Entry(
            message_frame,
            font=("Arial", 12, "bold")
        )
        title_entry.insert(0, title)
        title_entry.pack(
            fill="x",
            padx=8,
            pady=(8, 2)
        )

        timestamp_label = tk.Label(
            message_frame,
            text=f"Created: {timestamp}",
            anchor="w"
        )
        timestamp_label.pack(
            fill="x",
            padx=8
        )

        if last_updated is not None:
            last_updated_label = tk.Label(
                message_frame,
                text=f"Last updated: {last_updated}",
                anchor="w"
            )
            last_updated_label.pack(
                fill="x",
                padx=8,
                pady=(0, 5)
            )
        else:
            timestamp_label.pack_configure(
                pady=(0, 5)
            )



        text_frame = tk.Frame(message_frame)
        text_frame.pack(
            fill="x",
            padx=8,
            pady=(0, 8)
        )

        message_text = tk.Text(
            text_frame,
            height=4,
            wrap="word"
        )

        message_scrollbar = tk.Scrollbar(
            text_frame,
            orient="vertical",
            command=message_text.yview
        )

        message_text.configure(
            yscrollcommand=message_scrollbar.set
        )

        message_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        message_scrollbar.pack(
            side="right",
            fill="y"
        )

        message_text.insert("1.0", message)

        def scroll_message(event, message_text=message_text):
            message_text.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

            return "break"

        message_text.bind(
            "<MouseWheel>",
            scroll_message
        )

        button_frame = tk.Frame(message_frame)
        button_frame.pack(
            fill="x",
            padx=8,
            pady=(0, 8)
        )

        def on_save(
            message_id=message_id,
            title_entry=title_entry,
            message_text=message_text
        ):
            title = title_entry.get()
            text = message_text.get("1.0", "end-1c")

            database.update_message(
                message_id,
                title,
                text
            )

            load_messages(history_frame)

        save_button = tk.Button(
            button_frame,
            text="Save",
            command=on_save
        )
        save_button.pack(
            side="right",
            padx=(5, 0)
        )

        def on_delete(message_id=message_id):
            database.delete_message(message_id)
            load_messages(history_frame)

        delete_button = tk.Button(
            button_frame,
            text="Delete",
            command=on_delete
        )

        delete_button.pack(
            side="right"
        )


def create_post_area(post_frame, history_frame):
    title_label = tk.Label(
        post_frame,
        text="Title"
    )
    title_label.pack(anchor="w")

    title_entry = tk.Entry(post_frame)
    title_entry.pack(
        fill="x",
        pady=(0, 10)
    )

    message_label = tk.Label(
        post_frame,
        text="Message"
    )
    message_label.pack(anchor="w")

    message_text = tk.Text(
        post_frame,
        height=5,
        wrap="word"
    )
    message_text.pack(
        fill="x",
        pady=(0, 10)
    )

    countdown_label = tk.Label(post_frame, text="")
    countdown_label.pack()

    # Store the scheduled callback ID so the pending send can be cancelled.
    pending_send_id = None

    def finish_send():
        nonlocal pending_send_id
        pending_send_id = None

        title = title_entry.get()
        message = message_text.get("1.0", "end-1c")

        database.create_message(title, message)

        title_entry.configure(state="normal")
        message_text.configure(state="normal")
        title_entry.delete(0, "end")
        message_text.delete("1.0", "end")

        load_messages(history_frame)
        countdown_label.configure(text="")
        send_button.configure(text="Send", command=start_delayed_send)

    def update_countdown(seconds_left):
        """Update the label once per second, then complete the send."""
        nonlocal pending_send_id

        if seconds_left == 0:
            finish_send()
            return

        countdown_label.configure(text=f"Sending in {seconds_left}...")
        pending_send_id = post_frame.after(
            1000,
            update_countdown,
            seconds_left - 1
        )

    def start_delayed_send():
        # Ignore additional send attempts while a countdown is already active.
        if pending_send_id is not None:
            return
        # ensure messages cannot be sent with no content
        title = title_entry.get().strip()
        message = message_text.get("1.0", "end-1c").strip()
        if title == "" or message == "":
            return

        # Lock the inputs so the pending message cannot change before sending.
        title_entry.configure(state="disabled")
        message_text.configure(state="disabled")
        send_button.configure(text="Cancel", command=cancel_send)
        update_countdown(3)

    def cancel_send():
        """Stop the scheduled send and restore the input controls."""
        nonlocal pending_send_id

        if pending_send_id is not None:
            post_frame.after_cancel(pending_send_id)
            pending_send_id = None

        title_entry.configure(state="normal")
        message_text.configure(state="normal")
        countdown_label.configure(text="")
        send_button.configure(text="Send", command=start_delayed_send)

    def send_with_enter(event):
        start_delayed_send()
        # Prevent Tkinter from also inserting a newline for a normal Enter.
        return "break"

    def insert_new_line(event):
        message_text.insert(tk.INSERT, "\n")
        return "break"

    message_text.bind("<Return>", send_with_enter)
    message_text.bind("<Shift-Return>", insert_new_line)

    send_button = tk.Button(
        post_frame,
        text="Send",
        command=start_delayed_send
    )

    send_button.pack()
