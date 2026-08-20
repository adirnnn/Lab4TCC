# Laboratorio 4 - Teoria de la Computacion

## Video Link

https://youtu.be/yk8uWgVa-PI

## Parte 1: AFN con algoritmo de Thompson

El programa lee una expresion regular por linea desde `expresiones.txt`, construye el AFN equivalente usando el algoritmo de Thompson, crea un dibujo SVG de cada automata y simula una cadena asociada.

## Ejecucion

Se requiere Python 3.10 o superior, sin bibliotecas adicionales.

```powershell
cd C:\Users\28adr\Documents\Ciclo8\Lab4TCC
python main.py
```

Los resultados se imprimen como `si` o `no` y los grafos quedan en `salida\afn_1.svg` hasta `salida\afn_4.svg`.

## Formato de entradas

- `expresiones.txt`: una expresion por linea. Operadores soportados: union `|`, concatenacion implicita, estrella `*`, una o mas `+`, opcional `?`, parentesis y epsilon `ε`.
- `cadenas.txt`: una cadena por linea, en el mismo orden que las expresiones. Para probar otra cadena, cambia la linea correspondiente y vuelve a ejecutar.

El estado con doble circulo es el de aceptacion. La flecha verde señala el estado inicial; las aristas rotuladas `ε` son transiciones epsilon.
