# Multimodal Chat API Examples

The chat API now supports text, images, and documents. Here are examples of how to use these features:

## 1. Text-Only Message (Standard)

```json
POST /chat/
{
  "message": "What are the main features of this product?",
  "chat_id": null
}
```

## 2. Message with Image Analysis

```json
POST /chat/
{
  "message": "What's in this image?",
  "chat_id": null,
  "images": [
    {
      "type": "image",
      "format": "jpeg",
      "source": {
        "bytes": "<base64_encoded_image_string>"
      }
    }
  ]
}
```

## 3. Message with Multiple Images

```json
POST /chat/
{
  "message": "Compare these two screenshots",
  "chat_id": 1,
  "images": [
    {
      "type": "image",
      "format": "png",
      "source": {
        "bytes": "<base64_encoded_image_1>"
      }
    },
    {
      "type": "image",
      "format": "png",
      "source": {
        "bytes": "<base64_encoded_image_2>"
      }
    }
  ]
}
```

## 4. Message with Document Processing

```json
POST /chat/
{
  "message": "Summarize this document",
  "chat_id": null,
  "documents": [
    {
      "type": "document",
      "format": "pdf",
      "name": "report.pdf",
      "source": {
        "bytes": "<base64_encoded_pdf_string>"
      }
    }
  ]
}
```

## 5. Message with Both Images and Documents

```json
POST /chat/
{
  "message": "Analyze this chart from the PDF and the screenshot",
  "chat_id": 2,
  "images": [
    {
      "type": "image",
      "format": "png",
      "source": {
        "bytes": "<base64_encoded_screenshot>"
      }
    }
  ],
  "documents": [
    {
      "type": "document",
      "format": "pdf",
      "name": "financial_report.pdf",
      "source": {
        "bytes": "<base64_encoded_pdf>"
      }
    }
  ]
}
```

## Supported Formats

### Images
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

### Documents
- PDF (.pdf)
- CSV (.csv)
- Microsoft Word (.doc, .docx)
- Microsoft Excel (.xls, .xlsx)
- HTML (.html)
- Plain Text (.txt)
- Markdown (.md)

## Python Example: Sending Image with Base64 Encoding

```python
import base64
import requests

# Read and encode image
with open("screenshot.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

# Send request
response = requests.post(
    "http://localhost:8000/chat/",
    json={
        "message": "What does this screenshot show?",
        "chat_id": None,
        "images": [
            {
                "type": "image",
                "format": "png",
                "source": {"bytes": encoded_image}
            }
        ]
    }
)

print(response.json())
```

## JavaScript/TypeScript Example

```typescript
// Convert file to base64
async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64 = reader.result as string;
      // Remove data URL prefix (e.g., "data:image/png;base64,")
      const base64Data = base64.split(',')[1];
      resolve(base64Data);
    };
    reader.onerror = error => reject(error);
  });
}

// Send image with message
async function sendImageMessage(file: File, message: string) {
  const base64Image = await fileToBase64(file);
  const format = file.type.split('/')[1]; // e.g., "jpeg", "png"
  
  const response = await fetch('http://localhost:8000/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      chat_id: null,
      images: [
        {
          type: 'image',
          format: format,
          source: { bytes: base64Image }
        }
      ]
    })
  });
  
  return await response.json();
}

// Usage with file input
const fileInput = document.querySelector<HTMLInputElement>('#imageInput');
fileInput?.addEventListener('change', async (e) => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) {
    const result = await sendImageMessage(file, 'Analyze this image');
    console.log(result);
  }
});
```

## Features

- **Multimodal Support**: Process text, images, and documents together
- **Image Recognition**: Analyze screenshots, photos, diagrams, charts
- **Document Analysis**: Extract and analyze content from PDFs, spreadsheets, and other documents
- **Knowledge Base Integration**: Text-only queries use the knowledge base with RAG
- **Automatic Routing**: The API automatically selects the appropriate processing method based on content type
