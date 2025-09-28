# Configuration Files

This directory contains configuration files for the conversation simulator.

## Conversation Instructions

The conversation instructions are now externalized from the code for better security and maintainability.

### Files

- `conversation_instructions.yaml.example` - Template file with example configuration
- `conversation_instructions.yaml` - Actual configuration file (gitignored for security)
- `.gitignore` - Excludes sensitive configuration files from version control

### Setup

1. Copy the example file to create your configuration:

   ```bash
   cp conversation_instructions.yaml.example conversation_instructions.yaml
   ```

2. Customize the configuration as needed for your environment

3. The system will automatically load these instructions when starting conversations

### Security

- **Security instructions remain in code** to prevent tampering (prompt injection protection only)
- **Simulation instructions** are loaded from external files (configurable behavior)
- **Configuration files are gitignored** to prevent exposure in repositories
- **Session-specific delimiters** prevent prompt injection attacks
- **Modular instruction generation** ensures consistent security across all conversation types

### Configuration Structure

The YAML file contains:

- `conversation.core_simulation_instructions` - Core simulation behavior (most important)
- `conversation.purpose` - Overall conversation objective
- `conversation.additional_instructions` - List of behavior instructions
- `conversation.behavior_guidelines` - Guidelines for natural conversation
- `conversation.conversation_flow` - Steps for conversation progression
- `conversation.response_style` - Styling preferences (max sentences, tone, etc.)
- `conversation.context_awareness` - Guidelines for maintaining context

### Architecture

The instruction generation system has been refactored into modular functions for better maintainability:

- **`_generate_session_id()`** - Creates unique session identifiers for security
- **`_generate_security_prompt()`** - Generates security instructions with session-specific delimiters
- **`_build_instructions_with_template()`** - Constructs instructions using custom prompt templates
- **`_build_instructions_with_persona_details()`** - Builds instructions using persona characteristics
- **`get_instructions_for_persona()`** - Main orchestrator that combines all components

This modular approach ensures:

- **Consistent security** across all conversation types
- **Easy maintenance** and testing of individual components
- **Flexible instruction generation** for different persona configurations
- **Separation of concerns** between security, persona details, and conversation flow

### Fallback

If the configuration file is not found or fails to load, the system will use default instructions to ensure continued operation.
