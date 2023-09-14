import logging
from functools import partial
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from PIL import Image, ImageTk

from models.pdf_generator import PDFGenerator


class FEMAImageAttacher(ttk.Window):
    """A GUI for attaching additional images to a FEMA Elevation
    Certificate.

    Args:
        ttk.Window: A ttkbootstrap window.
    """

    ASTERISK_NOTE = "* Attachment page to FEMA Elevation Certificate"
    VIEWABLE_IMAGE_SIZE = (200, 200)
    PDF_SAVE_PATH = "test.pdf"

    def __init__(self):
        """Initializes the FEMAImageAttacher class."""
        super().__init__(title="FEMA Image Attacher")
        self.resizable(False, False)
        self.inputs = {}
        self.images = {}
        self.draw_widgets()

        # For testing purposes
        # for key, value in self.inputs.items():
        #     value.insert(0, key)

    def draw_widgets(self) -> None:
        """Draws the widgets for the FEMAImageAttacher class."""
        ttk.Label(self, text="FEMA Image Attacher", font=("Arial", 20)).pack(
            pady=15
        )
        self.draw_input_section()
        self.draw_image_attachment_section()

        button_font = ("Arial", 16, "bold")
        button_style = ttk.Style()
        button_style.configure("primary.TButton", font=button_font)
        generate_button = ttk.Button(
            self, text="Generate PDF", command=self.generate_pdf
        )
        generate_button.pack(pady=15, ipadx=10, ipady=5)
        generate_button.configure(style="primary.TButton")

    def draw_input_section(self) -> None:
        """Draws the input section of the FEMAImageAttacher class."""
        self.draw_label_entry(variable_name="file_number", label="File Number")
        self.draw_label_entry(variable_name="address", label="Property Address")
        self.draw_label_entry(variable_name="city", label="City")
        self.draw_label_entry(variable_name="zip_code", label="Zip Code")
        self.draw_label_entry(
            variable_name="note",
            label="Asterisk Note",
            default_entry_value=self.ASTERISK_NOTE,
        )

    def draw_label_entry(
        self,
        variable_name: str,
        label: str,
        default_entry_value: str = "",
    ) -> None:
        """Creates a label and entry widget.

        Args:
            variable_name (str): The name of the variable to store the
                entry value in.
            label (str): The label to display.
            default_entry_value (str, optional): The default value of
                the entry. Defaults to "".
        """

        row = ttk.Frame(self)
        row.pack(pady=5, padx=25)
        ttk.Label(row, text=label, width=20).pack(side="left")
        self.inputs[variable_name] = ttk.Entry(row, width=50)
        self.inputs[variable_name].pack(side="left", padx=5)

        if default_entry_value:
            self.inputs[variable_name].insert(0, default_entry_value)

    def draw_image_attachment_section(self) -> None:
        """Draws the image attachment section of the FEMAImageAttacher
        class.
        """
        attachment_row = ttk.Frame(self)
        attachment_row.pack(pady=15)
        self.draw_attachment_frame(attachment_row)
        self.draw_attachment_frame(attachment_row)

        attachment_row = ttk.Frame(self)
        attachment_row.pack(pady=15)
        self.draw_attachment_frame(attachment_row)
        self.draw_attachment_frame(attachment_row)

    def draw_attachment_frame(self, master: ttk.Frame) -> None:
        """Creates an attachment frame.

        Args:
            master (ttk.Frame): The master frame.
        """
        frame = ttk.Frame(master)
        frame.pack(side="left", padx=25)

        image_frame = ttk.Frame(frame, borderwidth=2, relief="groove")
        image_frame.pack()
        image_placeholder = ttk.Label(
            image_frame,
            text="Image Placeholder",
        )
        image_placeholder.pack(pady=90, padx=50)
        image_description = ttk.Entry(frame, width=30)
        image_description.pack(pady=5)

        button_frame = ttk.Frame(frame)

        attach_command = partial(
            self.attach_image, image_placeholder, image_description
        )
        attach_button = ttk.Button(
            frame, text="Attach Image", command=attach_command
        )

        clear_command = partial(
            self.clear_image, image_placeholder, image_description
        )
        clear_button = ttk.Button(
            frame, text="Clear Image", command=clear_command
        )

        attach_button.pack(side="left", padx=5)
        clear_button.pack(side="left", padx=5)
        button_frame.pack(pady=5)

    def attach_image(self, label: ttk.Label, description: ttk.Entry) -> None:
        """Attaches an image to the label.

        Args:
            label (ttk.Label): The label to attach the image to.
            description (ttk.Entry): The description of the image.
        """

        # PNG, JPG and JPEG files only
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        logging.info(f"File path: {file_path}")

        if file_path in self.images.keys():
            logging.info("Image already attached")
            self.error_popup("Image already attached")
            return

        if file_path:
            logging.info(f"Attaching image {file_path}")
            self.define_image(file_path, description)
            self.display_image(file_path, label)
            label.pack_configure(pady=0, padx=0)

        logging.debug(f"Images: {self.images}")

    def define_image(self, image_path: str, description: str) -> None:
        """Defines an image in the self.images attribute.

        Args:
            image_path (str): The path to the image.
            description (str): The description of the image.
        """

        self.images[image_path] = (
            self.resize_image_to_fit(image_path),
            description,
        )

    def display_image(self, image_path: str, label: ttk.Label = None) -> None:
        """Displays an image in the label.

        Args:
            image_path (str): The path to the image.
            label (ttk.Label, optional): The label to display the image
                in. Defaults to None.
        """
        # Set the image of the label to the self.images[image_path][0]
        image = self.images[image_path][0]
        if label:
            label.configure(image=image)
        else:
            ttk.Label(self, image=image).pack(pady=15)

    def clear_image(self, label: ttk.Label, description: ttk.Entry) -> None:
        """Clears an image from the label.

        Args:
            label (ttk.Label): The label to clear the image from.
            description (ttk.Entry): The description of the image.
        """
        logging.debug(f"Images: {self.images}")

        # Get the image path from the label
        for image_path, (_, entry) in self.images.items():
            if description == entry:
                logging.info(f"Clearing image {image_path}")
                self.images.pop(image_path, None)
                logging.info(f"{image_path} removed from self.images")
                break

        description.delete(0, "end")
        label.configure(image="")
        label.pack_configure(pady=90, padx=50)
        logging.debug(f"Images: {self.images}")

    def resize_image_to_fit(self, image_path: str) -> ImageTk.PhotoImage:
        """Resizes an image to the dimensions specified in the
        VIEWABLE_IMAGE_SIZE attribute.

        Args:
            image_path (str): The path to the image to resize.

        Returns:
            ImageTk.PhotoImage: The resized image.
        """
        logging.info(f"Resizing image {image_path}")
        img = Image.open(image_path)
        img = img.resize(self.VIEWABLE_IMAGE_SIZE)
        logging.info(f"Image resized to {self.VIEWABLE_IMAGE_SIZE}")
        return ImageTk.PhotoImage(img)

    def error_popup(self, message: str) -> None:
        """Displays an error popup.

        Args:
            message (str): The message to display in the popup.
        """
        messagebox.showerror("Error", message)

    def generate_pdf(self) -> None:
        """Generates a PDF."""

        logging.info("Generating PDF")
        for input in self.inputs.values():
            logging.info(f"Input: {input.get()}")
        pdf_generator = PDFGenerator(self.inputs, self.images)
        pdf_generator.generate_pdf(self.PDF_SAVE_PATH)

        logging.info(f"PDF saved to {self.PDF_SAVE_PATH}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = FEMAImageAttacher()
    app.mainloop()
