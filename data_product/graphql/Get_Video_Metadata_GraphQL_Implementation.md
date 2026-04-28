# StreamForge Video Metadata GraphQL API

**Version:** 1.0.0  
**Description:** GraphQL implementation of the Video Metadata Query port for the Video Data Product.

---

## Overview

This GraphQL API provides access to video metadata managed by the Video Data Product. It allows clients to query for specific fields and traverse relationships such as creator information.

---

## GraphQL Query

```graphql
query GetVideoMetadata($videoId: ID!) {
  video(id: $videoId) {
    videoId
    title
    creator {
      creatorId
      name
    }
    uploadDate
    durationSeconds
    genre
    maturityRating
  }
}
