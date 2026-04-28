# StreamForge Video Metadata REST/OpenAPI API

**Version:** 1.0.0  
**Description:** REST/OpenAPI implementation of the Video Metadata Query port for the Video Data Product.

---

## Overview

This REST API provides access to video metadata managed by the Video Data Product. It exposes a fixed HTTP endpoint that allows clients to retrieve metadata for a specific video by supplying a video identifier.

---

## OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: StreamForge Video Metadata API
  version: 1.0.0
  description: REST implementation of the Video Metadata Query port.

paths:
  /videos/{videoId}/metadata:
    get:
      summary: Get metadata for a video
      operationId: getVideoMetadata
      parameters:
        - name: videoId
          in: path
          required: true
          description: Unique identifier for the video.
          schema:
            type: string
      responses:
        "200":
          description: Video metadata was found.
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/VideoMetadata"
        "404":
          description: No video metadata was found for the supplied video identifier.

components:
  schemas:
    VideoMetadata:
      type: object
      required:
        - videoId
        - title
        - creatorId
        - uploadDate
      properties:
        videoId:
          type: string
        title:
          type: string
        creatorId:
          type: string
        uploadDate:
          type: string
          format: date-time
        durationSeconds:
          type: integer
        genre:
          type: string
        maturityRating:
          type: string
```

---

## Parameters

| Name    | Type   | Required | Description                     |
|---------|--------|----------|---------------------------------|
| videoId | string | Yes      | Unique identifier for the video |

---

## Example Request

```http
GET /videos/vid-12345/metadata
Accept: application/json
```

---

## Example Response

```json
{
  "videoId": "vid-12345",
  "title": "Introduction to Semantic Knowledge Graphs",
  "creatorId": "creator-678",
  "uploadDate": "2026-02-15T10:30:00Z",
  "durationSeconds": 420,
  "genre": "Education",
  "maturityRating": "G"
}
```

---

## Notes

- This API exposes a fixed REST endpoint for retrieving video metadata.
- The OpenAPI specification defines the request structure, response structure, datatypes, and status codes.
- The semantics of the returned data are defined by the Video Data Product ontology.
- This implementation realizes the same Video Metadata Query port as the GraphQL implementation, but uses a REST/OpenAPI interaction style.
