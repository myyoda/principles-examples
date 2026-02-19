---
title: "Accessible"
description: "Data should be retrievable via standardized protocols, with clear access conditions"
---

The Accessible principle requires that once data is found, users need to know how it can be accessed. This involves:

- Making data retrievable by their identifier using a standardized communication protocol.
- Ensuring the protocol is open, free, and universally implementable.
- Supporting authentication and authorization where necessary.
- Making metadata accessible even when the data itself is no longer available.

STAMPED supports accessibility through practices like using standard transfer protocols (HTTP, SSH), hosting data in established repositories, providing clear access documentation, and maintaining metadata independently of data availability. Tools like git-annex and DataLad enable flexible access to data across multiple storage backends while keeping a consistent interface.
