rm -f tortu.py
echo "import turtle as t" > tortu.py

cat turtle | sed 's/Tourne droite de \([0-9]*\).*/t.right(\1)/' | sed 's/Tourne gauche de \([0-9]*\).*/t.left(\1)/' | sed 's/Avance \([0-9]*\).*/t.forward(\1)/' | sed 's/Recule \([0-9]*\).*/t.backward(\1)/' | grep -v digest >> tortu.py

python tortu.py

