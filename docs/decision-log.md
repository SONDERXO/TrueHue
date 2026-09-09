# Decision Log

Track key technical and design decisions here.

| Date | Decision | Rationale | Alternatives considered |
|------|----------|-----------|------------------------|
| 2026-09-09 | Use CIELAB L*/b* for ITA computation | Standard formula from literature; directly maps to Fitzpatrick/MST scales | Direct RGB classification (less interpretable) |
| 2026-09-09 | Decision-tree regression for correction parameters | Lightweight, interpretable, fast inference on-device | Neural network (too heavy for on-device), linear regression (underfit) |
