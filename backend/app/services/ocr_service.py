"""
OCR Service
Handles Optical Character Recognition for document processing
"""

import base64
import io
from typing import Any, Dict, List, Optional

import pdf2image
import pytesseract
from loguru import logger
from PIL import Image

from app.core.config import get_settings

settings = get_settings()


class OCRService:
    """
    Service for extracting text from images and PDFs
    Uses Tesseract OCR for text extraction
    """

    def __init__(self):
        self.supported_image_formats = [
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tiff",
            ".webp",
        ]
        self.supported_pdf_format = ".pdf"
        self.default_language = "eng"

    async def process_image(
        self,
        image_data: bytes,
        language: str = "eng",
        config: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract text from image using OCR

        Args:
            image_data: Image file bytes
            language: OCR language (default: eng)
            config: Optional Tesseract config string

        Returns:
            Dict with extracted text and metadata

        Example:
            with open("document.jpg", "rb") as f:
                result = await ocr_service.process_image(f.read())
            print(result["text"])
        """
        try:
            logger.info("Processing image with OCR")

            # Load image
            image = Image.open(io.BytesIO(image_data))

            # Perform OCR
            if config:
                text = pytesseract.image_to_string(image, lang=language, config=config)
            else:
                text = pytesseract.image_to_string(image, lang=language)

            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image, lang=language, output_type=pytesseract.Output.DICT
            )

            # Calculate confidence score
            confidences = [
                int(conf) for conf in data["conf"] if conf != "-1" and int(conf) > 0
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            # Extract structured data
            words = []
            for i, word_text in enumerate(data["text"]):
                if word_text.strip():
                    words.append(
                        {
                            "text": word_text,
                            "confidence": int(data["conf"][i]),
                            "bbox": {
                                "x": data["left"][i],
                                "y": data["top"][i],
                                "width": data["width"][i],
                                "height": data["height"][i],
                            },
                        }
                    )

            result = {
                "text": text.strip(),
                "language": language,
                "confidence": round(avg_confidence, 2),
                "word_count": len(text.split()),
                "character_count": len(text),
                "words": words,
                "image_size": {
                    "width": image.width,
                    "height": image.height,
                },
            }

            logger.info(
                f"OCR completed. Extracted {result['word_count']} words with {result['confidence']}% confidence"
            )

            return result

        except Exception as e:
            logger.error(f"Image OCR processing failed: {str(e)}")
            raise

    async def extract_text(
        self,
        image_data: bytes,
        language: str = "eng",
    ) -> str:
        """
        Simple text extraction from image (convenience method)

        Args:
            image_data: Image file bytes
            language: OCR language

        Returns:
            Extracted text string

        Example:
            text = await ocr_service.extract_text(image_bytes)
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image, lang=language)
            return text.strip()

        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise

    async def process_pdf(
        self,
        pdf_data: bytes,
        language: str = "eng",
        dpi: int = 300,
    ) -> Dict[str, Any]:
        """
        Extract text from PDF using OCR

        Args:
            pdf_data: PDF file bytes
            language: OCR language
            dpi: DPI for PDF to image conversion (higher = better quality, slower)

        Returns:
            Dict with extracted text from all pages and metadata

        Example:
            with open("document.pdf", "rb") as f:
                result = await ocr_service.process_pdf(f.read())
            print(result["full_text"])
        """
        try:
            logger.info("Processing PDF with OCR")

            # Convert PDF to images
            images = pdf2image.convert_from_bytes(pdf_data, dpi=dpi)

            pages_data = []
            all_text = []

            # Process each page
            for page_num, image in enumerate(images, 1):
                logger.info(f"Processing PDF page {page_num}/{len(images)}")

                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format="PNG")
                img_bytes = img_byte_arr.getvalue()

                # Process page
                page_result = await self.process_image(img_bytes, language=language)

                pages_data.append(
                    {
                        "page_number": page_num,
                        "text": page_result["text"],
                        "confidence": page_result["confidence"],
                        "word_count": page_result["word_count"],
                    }
                )

                all_text.append(page_result["text"])

            # Combine all text
            full_text = "\n\n".join(all_text)

            # Calculate overall statistics
            avg_confidence = (
                sum(p["confidence"] for p in pages_data) / len(pages_data)
                if pages_data
                else 0
            )

            result = {
                "full_text": full_text,
                "page_count": len(images),
                "pages": pages_data,
                "language": language,
                "avg_confidence": round(avg_confidence, 2),
                "total_word_count": len(full_text.split()),
                "total_character_count": len(full_text),
            }

            logger.info(
                f"PDF OCR completed. Processed {result['page_count']} pages with {result['avg_confidence']}% confidence"
            )

            return result

        except Exception as e:
            logger.error(f"PDF OCR processing failed: {str(e)}")
            raise

    async def process_base64_image(
        self,
        base64_data: str,
        language: str = "eng",
    ) -> Dict[str, Any]:
        """
        Process base64 encoded image

        Args:
            base64_data: Base64 encoded image data
            language: OCR language

        Returns:
            OCR result dict

        Example:
            result = await ocr_service.process_base64_image(
                "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
            )
        """
        try:
            # Decode base64
            image_data = base64.b64decode(base64_data)

            # Process image
            return await self.process_image(image_data, language=language)

        except Exception as e:
            logger.error(f"Base64 image processing failed: {str(e)}")
            raise

    async def detect_language(self, image_data: bytes) -> str:
        """
        Detect language in image text

        Args:
            image_data: Image file bytes

        Returns:
            Detected language code

        Example:
            lang = await ocr_service.detect_language(image_bytes)
            print(f"Detected language: {lang}")
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            # Get OSD (Orientation and Script Detection)
            osd = pytesseract.image_to_osd(image)

            # Parse language from OSD output
            for line in osd.split("\n"):
                if "Script:" in line:
                    script = line.split(":")[1].strip()
                    return script

            return "eng"  # Default fallback

        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return "eng"

    async def extract_tables(self, image_data: bytes) -> List[List[str]]:
        """
        Extract table data from image (basic implementation)

        Args:
            image_data: Image file bytes

        Returns:
            List of rows, each row is a list of cell values

        Note:
            This is a basic implementation. For production use,
            consider using specialized libraries like table-transformer
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            # Use Tesseract TSV output for table structure
            tsv_data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT
            )

            # Group by line number
            lines = {}
            for i, text in enumerate(tsv_data["text"]):
                if text.strip():
                    line_num = tsv_data["line_num"][i]
                    if line_num not in lines:
                        lines[line_num] = []
                    lines[line_num].append(text)

            # Convert to list of rows
            table = [row for row in lines.values()]

            logger.info(f"Extracted table with {len(table)} rows")

            return table

        except Exception as e:
            logger.error(f"Table extraction failed: {str(e)}")
            raise

    async def preprocess_image(
        self,
        image_data: bytes,
        enhance_contrast: bool = True,
        denoise: bool = True,
        threshold: bool = True,
    ) -> bytes:
        """
        Preprocess image for better OCR results

        Args:
            image_data: Image file bytes
            enhance_contrast: Enhance image contrast
            denoise: Apply denoising filter
            threshold: Apply binary threshold

        Returns:
            Preprocessed image bytes

        Example:
            preprocessed = await ocr_service.preprocess_image(image_bytes)
            result = await ocr_service.process_image(preprocessed)
        """
        try:
            from PIL import ImageEnhance, ImageFilter

            image = Image.open(io.BytesIO(image_data))

            # Convert to grayscale
            image = image.convert("L")

            # Enhance contrast
            if enhance_contrast:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(2.0)

            # Denoise
            if denoise:
                image = image.filter(ImageFilter.MedianFilter(size=3))

            # Binary threshold
            if threshold:
                image = image.point(lambda x: 0 if x < 128 else 255, "1")

            # Convert back to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="PNG")

            return img_byte_arr.getvalue()

        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise

    async def check_health(self) -> bool:
        """
        Check if OCR service is available

        Returns:
            True if Tesseract is installed and working
        """
        try:
            # Try to get Tesseract version
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR version: {version}")
            return True

        except Exception as e:
            logger.error(f"OCR health check failed: {str(e)}")
            return False


# Global instance
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """
    Get singleton instance of OCR service

    Returns:
        OCRService instance
    """
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
