"""Laboratorio 4 - Construccion y simulacion de AFN mediante Thompson."""

from __future__ import annotations

import html
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

EPSILON = "ε"
CONCAT = "."


@dataclass
class Fragment:
    inicio: int
    aceptacion: int


class AFN:
    def __init__(self) -> None:
        self.transiciones: dict[int, list[tuple[str, int]]] = defaultdict(list)
        self._siguiente_estado = 0
        self.inicio = -1
        self.aceptacion = -1

    def nuevo_estado(self) -> int:
        estado = self._siguiente_estado
        self._siguiente_estado += 1
        return estado

    def agregar(self, origen: int, simbolo: str, destino: int) -> None:
        self.transiciones[origen].append((simbolo, destino))

    @property
    def estados(self) -> list[int]:
        return list(range(self._siguiente_estado))

    def cierre_epsilon(self, estados: set[int]) -> set[int]:
        cierre = set(estados)
        pendientes = list(estados)
        while pendientes:
            estado = pendientes.pop()
            for simbolo, destino in self.transiciones[estado]:
                if simbolo == EPSILON and destino not in cierre:
                    cierre.add(destino)
                    pendientes.append(destino)
        return cierre

    def acepta(self, cadena: str) -> bool:
        actuales = self.cierre_epsilon({self.inicio})
        for caracter in cadena:
            siguientes = {
                destino
                for estado in actuales
                for simbolo, destino in self.transiciones[estado]
                if simbolo == caracter
            }
            actuales = self.cierre_epsilon(siguientes)
        return self.aceptacion in actuales


def es_operando(token: str) -> bool:
    return token not in {"|", "*", "+", "?", "(", ")", CONCAT}


def tokenizar(expresion: str) -> list[str]:
    """Convierte la expresion a tokens e inserta concatenaciones explicitas."""
    expresion = expresion.replace(" ", "").replace("ε", EPSILON)
    crudos = list(expresion)
    if not crudos:
        raise ValueError("La expresion regular no puede estar vacia.")
    tokens: list[str] = []
    for token in crudos:
        if token not in {"|", "*", "+", "?", "(", ")"}:
            token = EPSILON if token == EPSILON else token
        if tokens:
            anterior = tokens[-1]
            if (es_operando(anterior) or anterior in {")", "*", "+", "?"}) and (
                es_operando(token) or token == "("
            ):
                tokens.append(CONCAT)
        tokens.append(token)
    return tokens


def postfija(expresion: str) -> list[str]:
    precedencia = {"|": 1, CONCAT: 2}
    salida: list[str] = []
    operadores: list[str] = []
    for token in tokenizar(expresion):
        if es_operando(token):
            salida.append(token)
        elif token in {"*", "+", "?"}:
            salida.append(token)  # operadores unarios, siempre posteriores
        elif token == "(":
            operadores.append(token)
        elif token == ")":
            while operadores and operadores[-1] != "(":
                salida.append(operadores.pop())
            if not operadores:
                raise ValueError("Parentesis desbalanceados.")
            operadores.pop()
        else:
            while (operadores and operadores[-1] != "(" and
                   precedencia[operadores[-1]] >= precedencia[token]):
                salida.append(operadores.pop())
            operadores.append(token)
    while operadores:
        operador = operadores.pop()
        if operador == "(":
            raise ValueError("Parentesis desbalanceados.")
        salida.append(operador)
    return salida


def construir_afn(expresion: str) -> AFN:
    afn = AFN()
    pila: list[Fragment] = []
    for token in postfija(expresion):
        if es_operando(token):
            inicio, fin = afn.nuevo_estado(), afn.nuevo_estado()
            afn.agregar(inicio, token, fin)
            pila.append(Fragment(inicio, fin))
        elif token == CONCAT:
            if len(pila) < 2: raise ValueError("Concatenacion invalida.")
            segundo, primero = pila.pop(), pila.pop()
            afn.agregar(primero.aceptacion, EPSILON, segundo.inicio)
            pila.append(Fragment(primero.inicio, segundo.aceptacion))
        elif token == "|":
            if len(pila) < 2: raise ValueError("Union invalida.")
            segundo, primero = pila.pop(), pila.pop()
            inicio, fin = afn.nuevo_estado(), afn.nuevo_estado()
            afn.agregar(inicio, EPSILON, primero.inicio); afn.agregar(inicio, EPSILON, segundo.inicio)
            afn.agregar(primero.aceptacion, EPSILON, fin); afn.agregar(segundo.aceptacion, EPSILON, fin)
            pila.append(Fragment(inicio, fin))
        else:
            if not pila: raise ValueError("Operador unario invalido.")
            fragmento = pila.pop()
            inicio, fin = afn.nuevo_estado(), afn.nuevo_estado()
            if token in {"*", "?"}: afn.agregar(inicio, EPSILON, fin)
            afn.agregar(inicio, EPSILON, fragmento.inicio)
            afn.agregar(fragmento.aceptacion, EPSILON, fin)
            if token in {"*", "+"}: afn.agregar(fragmento.aceptacion, EPSILON, fragmento.inicio)
            pila.append(Fragment(inicio, fin))
    if len(pila) != 1: raise ValueError("Expresion regular invalida.")
    resultado = pila.pop()
    afn.inicio, afn.aceptacion = resultado.inicio, resultado.aceptacion
    return afn


def guardar_svg(afn: AFN, destino: Path, titulo: str) -> None:
    """Dibuja el AFN como SVG sin dependencias externas."""
    total = len(afn.estados)
    ancho, alto = max(760, 130 * total), 330
    posiciones = {e: (80 + e * (ancho - 160) / max(1, total - 1), 165) for e in afn.estados}
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
              '<defs><marker id="flecha" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 Z" fill="#253858"/></marker></defs>',
              '<rect width="100%" height="100%" fill="#ffffff"/><text x="25" y="32" font-family="Arial" font-size="20" font-weight="bold">' + html.escape(titulo) + '</text>']
    for origen in afn.estados:
        for simbolo, destino_estado in afn.transiciones[origen]:
            x1, y1 = posiciones[origen]; x2, y2 = posiciones[destino_estado]
            if origen == destino_estado:
                partes.append(f'<path d="M{x1} {y1-23} C{x1-25} {y1-80}, {x1+25} {y1-80}, {x1+4} {y1-24}" fill="none" stroke="#253858" stroke-width="2" marker-end="url(#flecha)"/><text x="{x1}" y="{y1-62}" text-anchor="middle" font-family="Arial" font-size="16">{html.escape(simbolo)}</text>')
            else:
                direccion = 1 if x2 > x1 else -1
                partes.append(f'<line x1="{x1+direccion*25}" y1="{y1}" x2="{x2-direccion*27}" y2="{y2}" stroke="#253858" stroke-width="2" marker-end="url(#flecha)"/><text x="{(x1+x2)/2}" y="{y1-12}" text-anchor="middle" font-family="Arial" font-size="16" fill="#b42318">{html.escape(simbolo)}</text>')
    x, y = posiciones[afn.inicio]
    partes.append(f'<line x1="{x-65}" y1="{y}" x2="{x-27}" y2="{y}" stroke="#16803c" stroke-width="3" marker-end="url(#flecha)"/><text x="{x-65}" y="{y-12}" text-anchor="middle" font-family="Arial" font-size="14" fill="#16803c">inicio</text>')
    for estado in afn.estados:
        x, y = posiciones[estado]
        partes.append(f'<circle cx="{x}" cy="{y}" r="25" fill="#f5f8ff" stroke="#253858" stroke-width="2"/>')
        if estado == afn.aceptacion: partes.append(f'<circle cx="{x}" cy="{y}" r="20" fill="none" stroke="#16803c" stroke-width="2"/>')
        partes.append(f'<text x="{x}" y="{y+6}" text-anchor="middle" font-family="Arial" font-size="16">q{estado}</text>')
    partes.append('</svg>')
    destino.write_text("\n".join(partes), encoding="utf-8")


def leer_lineas(ruta: Path) -> list[str]:
    return [linea.strip() for linea in ruta.read_text(encoding="utf-8").splitlines() if linea.strip() and not linea.lstrip().startswith("#")]


def main() -> None:
    base = Path(__file__).resolve().parent
    archivo_expresiones = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "expresiones.txt"
    archivo_cadenas = Path(sys.argv[2]) if len(sys.argv) > 2 else base / "cadenas.txt"
    expresiones, cadenas = leer_lineas(archivo_expresiones), leer_lineas(archivo_cadenas)
    if len(expresiones) != len(cadenas):
        raise ValueError("Los archivos deben tener la misma cantidad de lineas (una cadena por expresion).")
    salida = base / "salida"; salida.mkdir(exist_ok=True)
    for indice, (expresion, cadena) in enumerate(zip(expresiones, cadenas), 1):
        afn = construir_afn(expresion)
        guardar_svg(afn, salida / f"afn_{indice}.svg", f"AFN {indice}: {expresion}")
        expresion_mostrada = expresion.replace(EPSILON, "epsilon")
        print(f"Expresion {indice}: {expresion_mostrada} | cadena: {cadena!r} -> {'si' if afn.acepta(cadena) else 'no'}")


if __name__ == "__main__":
    main()
