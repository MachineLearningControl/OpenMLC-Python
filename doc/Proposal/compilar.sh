#/bin/bash

nombre="Informe"
# Compilo dos veces para que aparezca el índice
pdflatex $nombre.tex
bibtex $nombre
pdflatex $nombre.tex
pdflatex $nombre.tex

# Borro los archivos auxiliares
rm $nombre.toc $nombre.aux $nombre.log $nombre.out $nombre.bbl $nombre.blg

