import logging
from typing import Dict, Tuple, Union

from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ttkbootstrap import Entry, PhotoImage


class PDFGenerator:
    """Generates a PDF file from a given text and image data."""

    IMAGE_DIMENSIONS = (275, 275)
    STATE = "FL"

    def __init__(
        self,
        text_data: Dict[Entry, Union[str, Entry]],
        image_data: Dict[str, Tuple[Union[PhotoImage, Entry]]],
        image_dimensions: Tuple[int, int] = IMAGE_DIMENSIONS,
    ) -> None:
        """Initializes the PDFGenerator class.

        Args:
            text_data (Dict[Entry, Union[str, Entry]]): A dict of text
                data.
            image_data (Dict[str, Tuple[Union[PhotoImage, Entry]]]): A
                dict of image data.
            image_dimensions (Tuple[int, int], optional): The dimensions
                of the images in the PDF. Defaults to IMAGE_DIMENSIONS.

        Raises:
            TypeError: If text_data or image_data are not of type dict.
        """

        try:
            self.validate_data(text_data, image_data, image_dimensions)
        except TypeError as error:
            logging.error(error)
            raise error

        self.text_data = self.parse_text_data(text_data)
        self.image_data = self.parse_image_data(image_data)
        self.image_dimensions = image_dimensions
        self.resize_images()
        self.pdf_dimensions = self.calculate_pdf_dimensions()

    def validate_data(
        self,
        text_data: Dict[Entry, Union[str, Entry]],
        image_data: Dict[str, Tuple[Union[PhotoImage, Entry]]],
        image_dimensions: Tuple[int, int],
    ) -> None:
        """Validates the text and image data. Raises TypeError if either
        is not a dict.

        Args:
            text_data (Dict[Entry, Union[str, Entry]]): A dict of text
                data.
            image_data (Dict[str, Tuple[Union[PhotoImage, Entry]]]): A
                dict of image data.
            image_dimensions (Tuple[int, int]): The dimensions of the
                images in the PDF.

        Raises:
            TypeError: If text_data is not a dict.
            TypeError: If image_data is not a dict.
        """
        if not isinstance(text_data, dict):
            raise TypeError(
                f"Expected text_data to be of type dict, got {type(text_data)}"
            )
        if not isinstance(image_data, dict):
            raise TypeError(
                f"Expected image_data to be a dict, got {type(image_data)}"
            )
        if not isinstance(image_dimensions, tuple):
            raise TypeError(
                f"Expected image_dimensions to be a tuple, got\
{type(image_dimensions)}"
            )

    def parse_text_data(
        self, text_data: Dict[Entry, Union[str, Entry]]
    ) -> dict:
        """Converts all text data to uppercase. Returns a new dict.

        Args:
            text_data (Dict[Entry, Union[str, Entry]]): A dict of text
                data.

        Returns:
            dict: A new dict with all text data converted to uppercase.

        Raises:
            TypeError: If any value in text_data is not of type str or
            Entry.
        """
        new_text_data = text_data.copy()
        for key, value in text_data.items():
            if isinstance(value, str):
                new_text_data[key] = value.upper()
            elif isinstance(value, Entry):
                new_text_data[key] = value.get().upper()
            else:
                raise TypeError(
                    f"Expected text_data value to be of type str or Entry,\
got {type(value)}"
                )

        city = new_text_data.get("city", None)
        zip_code = new_text_data.get("zip_code", None)
        if city and zip_code:
            new_text_data["city"] = f"{city}, {self.STATE}, {zip_code}"
            new_text_data.pop("zip_code")

        return new_text_data

    def parse_image_data(
        self, image_data: Dict[str, Tuple[Union[PhotoImage, Entry]]]
    ) -> dict:
        """Parses the image data to a format that can be used by the
        generate_pdf method.

        Args:
            image_data (Dict[str, Tuple[Union[PhotoImage, Entry]]]): A
                dict of image data.

        Returns:
            dict: A new dict of image data.
        """
        new_image_data = image_data.copy()
        for image_path, (image, entry) in image_data.items():
            new_image_data[image_path] = list((image, entry.get().upper()))

        return new_image_data

    def resize_image(self, image_path: str) -> Image:
        """Resizes an image to the dimensions specified in the
        image_dimensions attribute.

        Args:
            image_path (str): The path to the image to resize.

        Returns:
            Image: The resized image.
        """
        try:
            img = Image.open(image_path)
            logging.info(f"Resizing image {image_path}")
        except FileNotFoundError as error:
            logging.error(error)
            return

        return img.resize(self.image_dimensions)

    def resize_images(self) -> None:
        """Resizes all images in the image_data attribute."""
        for image_path in self.image_data.keys():
            self.image_data[image_path][0] = self.resize_image(image_path)

    def calculate_pdf_dimensions(self) -> Tuple[int, int]:
        """Calculates the dimensions of the PDF based on the number of
        images.

        Returns:
            Tuple[int, int]: The dimensions of the PDF.
        """
        num_images = len(self.image_data.keys())
        if num_images == 1:
            return self.image_dimensions
        elif num_images == 2:
            return (
                self.image_dimensions[0] * 2,
                self.image_dimensions[1],
            )
        elif num_images == 3:
            return (
                self.image_dimensions[0],
                self.image_dimensions[1] * 2,
            )
        elif num_images == 4:
            return (
                self.image_dimensions[0] * 2,
                self.image_dimensions[1] * 2,
            )

    def generate_pdf(self, save_path: str) -> None:
        """Generates a PDF based on the text and image data.

        Args:
            save_path (str): The path to save the PDF to.
        """
        pdf_canvas = canvas.Canvas(save_path, pagesize=letter)
        image_width, image_height = self.image_dimensions

        start_y = letter[1] - len(self.text_data.items()) * 20
        logging.debug(f"Start Y: {start_y}")

        padding_x = (letter[0] - image_width * 2) / 3
        padding_y = (start_y - image_height * 2) / 3
        logging.debug(f"Padding Y: {padding_y}")

        x = letter[0] / 2
        y = letter[1] - padding_y / 3
        for entry, text in self.text_data.items():
            y -= 20
            logging.debug(type(entry))
            logging.debug(entry)

            logging.debug(type(text))
            logging.debug(text)
            if entry == "note":
                y -= 5
            pdf_canvas.drawCentredString(x, y, text)

        pdf_canvas.line(padding_x, y + 15, letter[0] - padding_x, y + 15)
        pdf_canvas.line(padding_x, y - 5, letter[0] - padding_x, y - 5)

        # Place images in PDF

        x = padding_x
        y = start_y - padding_y

        for image_path, (image, description) in self.image_data.items():
            logging.debug(f"Y: {y}")
            if y <= padding_y:
                y = start_y - padding_y
                x += image_width + padding_x
            image.save(image_path)
            y -= image_height

            pdf_canvas.drawInlineImage(
                image_path, x, y, width=image_width, height=image_height
            )
            image_border = [
                (x, y, x + image_width, y),
                (x + image_width, y, x + image_width, y + image_height),
                (x + image_width, y + image_height, x, y + image_height),
                (x, y + image_height, x, y),
            ]
            pdf_canvas.lines(image_border)
            # Place centered description text below image
            pdf_canvas.drawCentredString(
                x + image_width / 2, y - 15, description
            )
            y -= padding_y

        # Save PDF
        pdf_canvas.save()
