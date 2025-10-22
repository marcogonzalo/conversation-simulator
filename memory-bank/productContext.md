# Product Context: Conversation Simulator

## Problem Statement

Muchos agentes de ventas carecen de oportunidades realistas y accesibles para practicar sus habilidades conversacionales. Los métodos tradicionales de entrenamiento (role-playing con compañeros, simulaciones básicas) no siempre ofrecen la inmersión, variedad de personalidades y feedback objetivo necesario para un aprendizaje efectivo. Esto resulta en profesionales de ventas que no están preparados para manejar diferentes tipos de clientes en situaciones reales.

## User Experience Goals

- **Conversación Natural**: Interacción fluida sin fricciones técnicas que permita al estudiante concentrarse en la técnica de venta
- **Personalidades Convincentes**: Clientes simulados que generen _engagement_ y desafíos realistas
- **Feedback Inmediato**: Análisis automático post-conversación que proporcione _insights_ accionables
- **Interfaz Excepcional**: UI limpia, atractiva, intuitiva, usable y accesible que promueva uso continuo
- **Inmersión Total**: Acentos regionales y características de voz y personalidad que hagan la experiencia más creíble
- **Simplicidad**: Diseño minimalista que elimine fricciones y facilite la adopción
- **Accesibilidad**: Cumplir estándares WCAG para usuarios con discapacidades
- **Respuesta Rápida**: Conversación ágil con respuestas de IA en <1.2 segundos después de que el usuario termine de hablar
- **Calidad de Audio**: Audio claro sin distorsiones ni interrupciones durante conversaciones largas

## Success Metrics

- **Engagement**: Tiempo promedio de conversación >5 minutos
- **Completitud**: Tasa de finalización de conversaciones >80%
- **Satisfacción**: Feedback positivo sobre naturalidad y utilidad
- **Retención**: Usuarios que regresan para múltiples sesiones
- **Aprendizaje**: Mejora observable en técnicas de venta entre sesiones
- **Usabilidad**: Tiempo de onboarding <2 minutos
- **Accesibilidad**: Cumplimiento de estándares WCAG 2.1 AA
- **Adopción**: Tasa de abandono en primera sesión <20%

## Sales Analysis Metrics

### 1. Métricas de Apertura y Calificación

#### Tasa de Preguntas Abiertas

- **Definición**: Porcentaje de preguntas que invitan al cliente a hablar más vs preguntas de sí/no
- **Objetivo**: >70% de preguntas abiertas
- **Medición**: Análisis de patrones de pregunta en la conversación
- **Indicador**: Habilidad para descubrir necesidades vs presentar producto

#### Tiempo de Escucha vs. Habla

- **Ratio Ideal**: 70% escucha / 30% habla
- **Medición**: Análisis de duración de turnos de conversación
- **Indicador**: Enfoque en entender al cliente vs vender
- **Algoritmo**: STT + análisis de pausas y turnos

#### Identificación de Pain Point

- **Definición**: ¿El vendedor identificó la necesidad real del cliente?
- **Medición**: Comparación entre resumen del estudiante vs necesidad real del perfil
- **Escala**: Binaria (sí/no) o cualitativa (1-5)
- **Momento**: Evaluación al final de la sesión

### 2. Métricas de Presentación y Manejo de Objeciones

#### Puntos de Valor Conectados

- **Definición**: Vinculación de características del producto a necesidades identificadas
- **Ejemplo**: "El módulo de reportes te ayudará a ver tus datos en tiempo real, lo que sé que es importante para ti"
- **Medición**: Análisis de coherencia entre necesidades identificadas y argumentos de venta
- **Escala**: 1-5 (pertinencia de argumentos)

#### Manejo Exitoso de Objeciones

- **Definición**: Reconocimiento y respuesta efectiva a objeciones del cliente
- **Medición**: Binaria (sí/no) por objeción o escala 1-5 por calidad
- **Algoritmo**: Detección de objeciones + análisis de respuestas
- **Indicador**: Capacidad de superar resistencia del cliente

#### Uso de Evidencia

- **Definición**: Utilización de datos, testimonios o casos de éxito
- **Medición**: Detección de referencias a pruebas, datos, testimonios
- **Indicador**: Fortalecimiento de credibilidad y toma de decisiones
- **Escala**: Frecuencia y relevancia del uso de evidencia

### 3. Métricas de Cierre y Próximos Pasos

#### Intención de Cierre

- **Definición**: Al menos un intento de cerrar la venta o establecer próximo paso
- **Medición**: Detección de frases de cierre en la conversación
- **Indicador**: Proactividad en el cierre de ventas
- **Escala**: Binaria (sí/no) + frecuencia de intentos

#### Cierre Exitoso

- **Definición**: Cliente simulado acepta la propuesta y "compra"
- **Medición**: Análisis de respuesta final del cliente simulado
- **Indicador**: Efectividad general de la presentación
- **Escala**: Binaria (sí/no) + nivel de compromiso

#### Definición de Próximos Pasos

- **Definición**: Establecimiento de acción concreta si no se cierra inmediatamente
- **Medición**: Detección de compromisos específicos y fechas
- **Indicador**: Profesionalismo y seguimiento estructurado
- **Escala**: Binaria (sí/no) + especificidad del próximo paso

## Target Users

- **Estudiantes de ventas**: Personas aprendiendo técnicas de venta
- **Agentes de ventas profesionales**: Vendedores que buscan mejorar sus habilidades
- **Profesionales junior**: Vendedores con poca experiencia
- **Vendedores senior**: Profesionales que quieren perfeccionar técnicas específicas
- **Instructores de ventas**: Educadores que buscan herramientas de práctica
- **Empresas de capacitación**: Organizaciones que entrenan equipos de ventas

## Value Proposition

"Practica técnicas de venta con clientes simulados por IA que hablan con acentos reales y personalidades convincentes. Implementa técnicas para manejar objeciones, mejorar tus habilidades de venta y ganar confianza. Recibe feedback cuantificable que permita un proceso de venta con resultados positivos."

## Competitive Advantage

- **Acentos regionales**: Pocos simuladores ofrecen esta característica
- **IA avanzada**: Personalidades más convincentes que scripts predefinidos
- **Feedback automático**: Análisis objetivo de la conversación
- **Experiencia conversacional**: Enfoque en voz vs texto
- **Escalabilidad**: Fácil agregar nuevos perfiles y características
