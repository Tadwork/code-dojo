import {
  generateDisplayName,
  generateUserId,
  getParticipantInfo,
  hexToRgba,
  sanitizeForCssContent,
} from "../participantUtils";

describe("participantUtils", () => {
  beforeEach(() => {
    localStorage.clear();
    window.crypto = {
      randomUUID: jest.fn(() => "123e4567-e89b-12d3-a456-426614174000"),
    };
  });

  afterEach(() => {
    delete window.crypto;
  });

  describe("generateUserId", () => {
    it("returns the stored id when present", () => {
      localStorage.setItem("codedojo_user_id", "existing-id");

      expect(generateUserId()).toBe("existing-id");
    });

    it("uses crypto.randomUUID and persists the generated id", () => {
      const userId = generateUserId();

      expect(userId).toBe("123e4567-e89b-12d3-a456-426614174000");
      expect(localStorage.getItem("codedojo_user_id")).toBe(userId);
    });
  });

  describe("generateDisplayName", () => {
    it("returns the stored display name when present", () => {
      localStorage.setItem("codedojo_display_name", "Stored Name");

      expect(generateDisplayName()).toBe("Stored Name");
    });

    it("generates and stores a display name", () => {
      const displayName = generateDisplayName();

      expect(displayName.split(" ")).toHaveLength(2);
      expect(localStorage.getItem("codedojo_display_name")).toBe(displayName);
    });
  });

  describe("getParticipantInfo", () => {
    it("returns both a userId and displayName", () => {
      expect(getParticipantInfo()).toEqual({
        userId: "123e4567-e89b-12d3-a456-426614174000",
        displayName: expect.any(String),
      });
    });
  });

  describe("hexToRgba", () => {
    it("converts a valid hex value with alpha", () => {
      expect(hexToRgba("#FF6B6B", 0.5)).toBe("rgba(255, 107, 107, 0.5)");
    });

    it("supports hex values without a leading hash", () => {
      expect(hexToRgba("4ECDC4", 1)).toBe("rgba(78, 205, 196, 1)");
    });

    it("falls back to black for invalid hex values", () => {
      expect(hexToRgba("BAD", 0.25)).toBe("rgba(0, 0, 0, 0.25)");
    });
  });

  describe("sanitizeForCssContent", () => {
    it("escapes quotes and backslashes for CSS content strings", () => {
      expect(sanitizeForCssContent(`'; \\"test"`)).toBe("\\'; \\\\\\\"test\\\"");
    });
  });
});
