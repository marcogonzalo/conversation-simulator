/**
 * Message role enumeration for consistent role handling across the application.
 */
export enum MessageRole {
  USER = "user",
  ASSISTANT = "ai",
  SYSTEM = "system"
}

/**
 * Type-safe message role values.
 */
export type MessageRoleValue = `${MessageRole}`;

/**
 * Helper functions for message role operations.
 */
export const MessageRoleUtils = {
  /**
   * Check if a role is a valid message role.
   */
  isValid(role: string): role is MessageRoleValue {
    return Object.values(MessageRole).includes(role as MessageRole);
  },

  /**
   * Get the display name for a role.
   */
  getDisplayName(role: MessageRoleValue): string {
    switch (role) {
      case MessageRole.USER:
        return "Usuario";
      case MessageRole.ASSISTANT:
        return "AI";
      case MessageRole.SYSTEM:
        return "Sistema";
      default:
        return "Desconocido";
    }
  },

  /**
   * Get the CSS class for a role.
   */
  getCSSClass(role: MessageRoleValue): string {
    switch (role) {
      case MessageRole.USER:
        return "user-message";
      case MessageRole.ASSISTANT:
        return "ai-message";
      case MessageRole.SYSTEM:
        return "system-message";
      default:
        return "unknown-message";
    }
  }
};
