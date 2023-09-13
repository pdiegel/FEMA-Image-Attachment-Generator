from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
import ttkbootstrap as ttk
from tkinter import filedialog

img_height = 450
img_width = 450


# Resize images to 450x450 px
def resize_image(image_path):
    img = Image.open(image_path)
    img = img.resize((img_width, img_height))
    return img


# Paths to your 4 images
texts = ["text1", "text2", "text3", "text4"]
image_paths = ["img.png", "img.png", "img.png", "img.png"]
resized_images = [resize_image(p) for p in image_paths]


# Add padding between images
padding = 50

# Calculate PDF dimensions
# 2 images wide and 2 images high, each 450 px plus padding between them
pdf_width = 2 * img_width + padding * 3
pdf_height = 2 * img_height + padding * 3

# Position for the 1st image (lower-left corner)
x, y = padding, img_height + padding * 2

# Create a PDF using reportlab
c = canvas.Canvas("output.pdf", pagesize=(pdf_width, pdf_height))

for i, (img, text) in enumerate(zip(resized_images, texts)):
    # Convert PIL Image to reportlab Image
    img_path = f"temp_img{i}.png"
    img.save(img_path)

    # Place image on PDF
    c.drawInlineImage(img_path, x, y, width=img_width, height=img_height)

    # Place text above image
    c.drawAlignedString(x, y + img_height + 10, text)

    # Adjust x and y coordinates
    if i == 0:  # Move right for the 2nd image
        x += img_width + padding
    elif i == 1:  # Move down and left for the 3rd image
        x = 50
        y -= img_height + padding
    elif i == 2:  # Move right for the 4th image
        x += img_width + padding

# Save PDF
c.save()


class FEMAImageAttacher(ttk.Window):
    STATE = "FL"
    ASTERISK_NOTE = "* Attachment page to FEMA Elevation Certificate"
    VIEWABLE_IMAGE_SIZE = (200, 200)

    def __init__(self):
        super().__init__(title="FEMA Image Attacher")
        self.resizable(False, False)
        self.inputs = {}
        self.images = {}
        self.draw_widgets()

    def draw_widgets(self):
        ttk.Label(self, text="FEMA Image Attacher", font=("Arial", 20)).pack(
            pady=15
        )
        self.draw_input_section()
        self.draw_image_attachment_section()

        # self.define_image("img.png")
        # self.display_image()

    def draw_input_section(self):
        self.create_label_entry(
            variable_name="file_number", label="File Number"
        )
        self.create_label_entry(
            variable_name="address", label="Property Address"
        )
        self.create_label_entry(variable_name="city", label="City")
        self.create_label_entry(variable_name="zip_code", label="Zip Code")
        self.create_label_entry(
            variable_name="note",
            label="Asterisk Note",
            default_entry_value=self.ASTERISK_NOTE,
        )

    def draw_image_attachment_section(self):
        attachment_row = ttk.Frame(self)
        attachment_row.pack(pady=15)
        self.create_attachment_frame(attachment_row)
        self.create_attachment_frame(attachment_row)

        attachment_row = ttk.Frame(self)
        attachment_row.pack(pady=15)
        self.create_attachment_frame(attachment_row)
        self.create_attachment_frame(attachment_row)

    def create_attachment_frame(self, master: ttk.Frame):
        frame = ttk.Frame(master)
        frame.pack(side="left", padx=25, pady=10)

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
        attach_button = ttk.Button(
            frame,
            text="Attach Image",
            command=lambda label=image_placeholder: self.attach_image(label),
        )
        clear_button = ttk.Button(
            frame,
            text="Clear Image",
            command=lambda label=image_placeholder: self.clear_image(label),
        )
        attach_button.pack(side="left", padx=5)
        clear_button.pack(side="left", padx=5)
        button_frame.pack(pady=5)

    def attach_image(self, label: ttk.Label):
        file_path = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
        if file_path:
            self.define_image(file_path)
            self.display_image(file_path, label)
            label.pack_configure(pady=0, padx=0)

    def define_image(self, image_path: str):
        self.images[image_path] = self.resize_image_to_fit(image_path)

    def display_image(self, image_path: str, label: ttk.Label = None):
        # Set the image of the label to the self.images[image_index]
        if label:
            label.configure(image=self.images[image_path])
        else:
            ttk.Label(self, image=self.images[image_path]).pack(pady=15)

    def clear_image(self, label: ttk.Label):
        label.configure(image="")
        label.pack_configure(pady=90, padx=50)

    def resize_image_to_fit(self, image_path: str):
        img = Image.open(image_path)
        img = img.resize(self.VIEWABLE_IMAGE_SIZE)
        return ImageTk.PhotoImage(img)

    def create_label_entry(
        self,
        variable_name: str,
        label: str,
        default_entry_value: str = "",
    ):
        row = ttk.Frame(self)
        row.pack(pady=5, padx=25)
        ttk.Label(row, text=label, width=20).pack(side="left")
        self.inputs[variable_name] = ttk.Entry(row, width=50)
        self.inputs[variable_name].pack(side="left", padx=5)

        if default_entry_value:
            self.inputs[variable_name].insert(0, default_entry_value)


if __name__ == "__main__":
    app = FEMAImageAttacher()
    app.mainloop()
