# SKG Diagramming Style — Shape Legend

This document defines the canonical notation used throughout *Semantic Knowledge Graph Design*.

## Shapes

### **Data Product**
- **Rounded Rectangle**
- Color: Steel-blue `#607D8B`
- Represents a bounded data artifact (API, dataset, SKG endpoint)

### **Microservice / Software Component**
- **Oval (Pill Shape)**
- Color: Olive-gray `#8D8F6F`
- Represents an operational service or computational module

### **Aggregate / Derived Computation**
- **Octagon**
- Color: Slate-purple `#6C648B`
- Represents an aggregation, transformation, or computational process

### **Domain Boundary**
- **Ellipse (outline only)**
- Outline Color: Sand `#C7B299`
- Groups related elements into a conceptual or organizational domain

## Connectors

### **Data Flow**
- Solid line with arrowhead

### **API / Event Flow**
- Dotted line with arrowhead

## Color Usage
Color is optional and must not convey information that cannot also be seen in grayscale.

## Layout Rules
- Flow direction: Left → Right or Top → Bottom
- Avoid circular/radial layouts
- Use ample whitespace
- No overlapping colored regions or watercolor-style fills

## Typography
- Sans-serif (Calibri, Segoe UI, Helvetica)
- 11 pt minimum inside shapes
