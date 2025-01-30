I've been asked about this a couple of times, so here is a codesys plaintext exporter for using with git and other text based version control systems. It converts POUs/DUTs/ other text-friendly objects into text formats. I chose to split the declaration and implementation into separate files, with .DEC.exp and .IMP.exp extensions.

SFC, LD, and CFC pous that can't be simply exported as text are exported as XML. Import is not written yet, and left as an exercise to the reader.

Consider this as academic crapware - it's poorly written with inconsistent naming conventions, and may not work for you. Use at your own risk.
