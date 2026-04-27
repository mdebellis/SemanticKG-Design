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
