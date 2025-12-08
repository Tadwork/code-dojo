import axios from 'axios';
import { createSession, getSession, executeCode, generateCode } from '../api';

jest.mock('axios');

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createSession', () => {
    it('should create a session with title and language', async () => {
      const mockResponse = {
        data: {
          id: 'test-id',
          session_code: 'TEST1234',
          title: 'Test Session',
          language: 'python',
          code: '',
          created_at: '2024-01-01T00:00:00',
          active_users: 0,
        },
      };

      axios.post.mockResolvedValue(mockResponse);

      const result = await createSession('Test Session', 'python');

      expect(axios.post).toHaveBeenCalledWith('/api/sessions', {
        title: 'Test Session',
        language: 'python',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should create a session with default language', async () => {
      const mockResponse = {
        data: {
          session_code: 'TEST1234',
          language: 'python',
        },
      };

      axios.post.mockResolvedValue(mockResponse);

      await createSession('Test Session');

      expect(axios.post).toHaveBeenCalledWith('/api/sessions', {
        title: 'Test Session',
        language: 'python',
      });
    });

    it('should handle errors when creating session', async () => {
      const error = new Error('Network error');
      axios.post.mockRejectedValue(error);

      await expect(createSession('Test Session')).rejects.toThrow('Network error');
    });
  });

  describe('getSession', () => {
    it('should get a session by code', async () => {
      const mockResponse = {
        data: {
          id: 'test-id',
          session_code: 'TEST1234',
          title: 'Test Session',
          language: 'python',
          code: 'print("hello")',
          created_at: '2024-01-01T00:00:00',
          active_users: 0,
        },
      };

      axios.get.mockResolvedValue(mockResponse);

      const result = await getSession('TEST1234');

      expect(axios.get).toHaveBeenCalledWith('/api/sessions/TEST1234');
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle errors when getting session', async () => {
      const error = new Error('Session not found');
      axios.get.mockRejectedValue(error);

      await expect(getSession('INVALID')).rejects.toThrow('Session not found');
    });
  });

  describe('executeCode', () => {
    it('should execute code successfully', async () => {
      const mockResponse = {
        data: {
          output: 'Hello World\n',
          error: '',
        },
      };

      axios.post.mockResolvedValue(mockResponse);

      const result = await executeCode('print("Hello World")', 'python');

      expect(axios.post).toHaveBeenCalledWith('/api/execute', {
        code: 'print("Hello World")',
        language: 'python',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle execution errors', async () => {
      const error = new Error('Execution failed');
      axios.post.mockRejectedValue(error);

      await expect(executeCode('invalid code', 'python')).rejects.toThrow('Execution failed');
    });
  });

  describe('generateCode', () => {
    it('should generate code successfully', async () => {
      const mockResponse = {
        data: {
          code: 'def add(a, b):\n    return a + b',
          error: '',
        },
      };

      axios.post.mockResolvedValue(mockResponse);

      const result = await generateCode('Create an add function', '', 'python');

      expect(axios.post).toHaveBeenCalledWith('/api/assistant/generate', {
        prompt: 'Create an add function',
        code: '',
        language: 'python',
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should generate code with existing code context', async () => {
      const mockResponse = {
        data: {
          code: 'def add(a, b):\n    # Modified\n    return a + b',
          error: '',
        },
      };

      axios.post.mockResolvedValue(mockResponse);

      const result = await generateCode(
        'Add a comment',
        'def add(a, b):\n    return a + b',
        'python'
      );

      expect(axios.post).toHaveBeenCalledWith('/api/assistant/generate', {
        prompt: 'Add a comment',
        code: 'def add(a, b):\n    return a + b',
        language: 'python',
      });
      expect(result.code).toContain('Modified');
    });

    it('should handle AI generation errors', async () => {
      const error = new Error('AI service unavailable');
      axios.post.mockRejectedValue(error);

      await expect(generateCode('Create something', '', 'python')).rejects.toThrow(
        'AI service unavailable'
      );
    });
  });
});
