# Project Brief: Conversation Simulator

## Overview

Desarrollar un simulador de clientes para que agentes de ventas puedan practicar y mejorar sus habilidades interactuando con una IA que simule a un potencial comprador con un perfil y personalidad específica. El vendedor tendrá la oportunidad de implementar técnicas de ventas para manejar objeciones, ganar confianza y tener un feedback cuantificable que permita un proceso de venta con resultados positivos. La experiencia se centra en conversaciones de voz naturales con diferentes perfiles de clientes simulados, utilizando acentos regionales para mayor inmersión.

## Core Requirements

- Conversación de voz bidireccional en tiempo real con latencia <500ms
- Múltiples perfiles de cliente con personalidades distintivas y acentos regionales
- Análisis automático post-conversación con feedback detallado y accionable
- Recomendaciones personalizadas de contenido educativo basado en performance
- Interfaz minimalista enfocada en la experiencia conversacional
- Sistema de finalización inteligente (natural o manual)

## Goals

- **Validar la experiencia conversacional** como propuesta de valor principal
- **Crear un MVP funcional** que demuestre la calidad de la interacción
- **Establecer base para escalabilidad** futura (panel admin, avatares digitales)
- **Captar usuarios tempranos** para validación del producto y feedback

## Project Scope

### In Scope (MVP)

- 3-5 perfiles de persona básicos con acentos regionales
- Conversación de voz fluida usando OpenAI Realtime API (audio-to-audio en tiempo real)
- Motor de personalidades integrado en OpenAI Realtime API
- Análisis automático y reportes básicos
- UI minimalista para selección de persona y conversación
- Sistema de recomendaciones de contenido educativo

### Out of Scope (Futuro)

- Panel de administración completo para gestión de perfiles
- Avatares digitales animados
- Métricas avanzadas y analytics
- Sistema de usuarios y autenticación
- Múltiples idiomas (inicialmente solo español)
- Integración con LMS o plataformas educativas

## Success Criteria

- Tiempo promedio de conversación de prueba: 5-8 minutos (optimizado para validación)
- Conversaciones reales: 10-15 minutos (cuando el producto esté maduro)
- Tasa de finalización de conversaciones >80%
- Satisfacción del usuario con la experiencia conversacional
- Retención de usuarios para múltiples sesiones
- Feedback positivo sobre la naturalidad de las personalidades
- Capacidad de manejar conversaciones largas sin degradación de performance
