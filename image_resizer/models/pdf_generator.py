import logging
from typing import Dict, List, Tuple, Union

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
        text_data: Dict[str, Union[str, Entry]],
        image_data: Dict[str, Tuple[PhotoImage, Entry]],
        image_dimensions: Tuple[int, int] = IMAGE_DIMENSIONS,
    ) -> None:
        """Initializes the PDFGenerator class.

        Args:
            text_data (Dict[str, Union[str, Entry]]): A dict of text
                data.
            image_data Dict[str, Tuple[PhotoImage, Entry]]): A
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

    def validate_data(
        self,
        text_data: Dict[str, Union[str, Entry]],
        image_data: Dict[str, Tuple[PhotoImage, Entry]],
        image_dimensions: Tuple[int, int],
    ) -> None:
        """Validates the text and image data. Raises TypeError if either
        is not a dict.

        Args:
            text_data (Dict[str, Union[str, Entry]]): A dict of text
                data.
            image_data Dict[str, Tuple[PhotoImage, Entry]]): A
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
        self, text_data: Dict[str, Union[str, Entry]]
    ) -> Dict[str, str]:
        """Converts all text data to uppercase. Returns a new dict.

        Args:
            text_data (Dict[str, Union[str, Entry]]): A dict of text
                data.

        Returns:
            Dict[str, str]: A new dict with all text data converted to
                uppercase.

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
        self, image_data: Dict[str, Tuple[PhotoImage, Entry]]
    ) -> Dict[str, List[Union[PhotoImage, str]]]:
        """Parses the image data to a format that can be used by the
        generate_pdf method.

        Args:
            image_data Dict[str, Tuple[PhotoImage, Entry]]): A
                dict of image data.

        Returns:
            Dict[str, List[Union[PhotoImage, str]]]: A dict of image
                data.
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
        logging.debug(f"Image data before resizing: {self.image_data}")
        for image_path in self.image_data.keys():
            self.image_data[image_path][0] = self.resize_image(image_path)
        logging.debug(f"Image data after resizing: {self.image_data}")

    def generate_pdf(self, save_path: str) -> None:
        """Generates a PDF based on the text and image data.

        Args:
            save_path (str): The path to save the PDF to.
        """
        pdf_canvas = canvas.Canvas(save_path, pagesize=letter)
        image_width, image_height = self.image_dimensions

        start_y = letter[1] - len(self.text_data.items()) * 20
        padding_x = (letter[0] - image_width * 2) / 3
        padding_y = (start_y - image_height * 2) / 3

        self.draw_text(pdf_canvas, padding_y)
        self.draw_lines(pdf_canvas, start_y - 23, padding_x)
        self.draw_images(
            pdf_canvas, start_y, padding_x, padding_y, image_width, image_height
        )

        pdf_canvas.save()

    def draw_text(self, pdf_canvas: canvas.Canvas, padding_y: int) -> None:
        """Draws text to the PDF.

        Args:
            pdf_canvas (canvas.Canvas): The PDF canvas.
            y (int): The y coordinate.
        """
        x = letter[0] / 2
        y = letter[1] - padding_y / 3
        for entry, text in self.text_data.items():
            y -= 20
            if entry == "note":
                y -= 5
            pdf_canvas.drawCentredString(x, y, text)

    def draw_lines(
        self, pdf_canvas: canvas.Canvas, y: int, padding_x: int
    ) -> None:
        """Draws lines to the PDF.

        Args:
            pdf_canvas (canvas.Canvas): The PDF canvas.
            y (int): The y coordinate.
            padding_x (int): The x padding.
        """
        pdf_canvas.line(padding_x, y + 15, letter[0] - padding_x, y + 15)
        pdf_canvas.line(padding_x, y - 5, letter[0] - padding_x, y - 5)

    def draw_images(
        self,
        pdf_canvas: canvas.Canvas,
        start_y: int,
        padding_x: int,
        padding_y: int,
        image_width: int,
        image_height: int,
    ) -> None:
        """Draws images to the PDF.

        Args:
            pdf_canvas (canvas.Canvas): The PDF canvas.
            start_y (int): The starting y coordinate.
            padding_x (int): The x padding.
            padding_y (int): The y padding.
            image_width (int): The image width.
            image_height (int): The image height.
        """
        x = padding_x
        y = start_y - padding_y
        for image_path, (image, description) in self.image_data.items():
            if y <= padding_y:
                y = start_y - padding_y
                x += image_width + padding_x
            image.save(image_path)
            y -= image_height
            pdf_canvas.drawInlineImage(
                image_path, x, y, width=image_width, height=image_height
            )
            self.draw_image_border(pdf_canvas, x, y, image_width, image_height)
            pdf_canvas.drawCentredString(
                x + image_width / 2, y - 15, description
            )
            y -= padding_y

    def draw_image_border(
        self,
        pdf_canvas: canvas.Canvas,
        x: int,
        y: int,
        image_width: int,
        image_height: int,
    ) -> None:
        """Draws a border around an image.

        Args:
            pdf_canvas (canvas.Canvas): The PDF canvas.
            x (int): The x coordinate.
            y (int): The y coordinate.
            image_width (int): The image width.
            image_height (int): The image height.
        """
        image_border = [
            (x, y, x + image_width, y),
            (x + image_width, y, x + image_width, y + image_height),
            (x + image_width, y + image_height, x, y + image_height),
            (x, y + image_height, x, y),
        ]
        pdf_canvas.lines(image_border)
