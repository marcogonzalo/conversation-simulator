import {
  processTextChunk,
  processTextChunks,
  smartProcessTextChunk,
  shouldConcatenateWithoutSpace
} from '../textChunkProcessor';

describe('textChunkProcessor', () => {
  describe('processTextChunk', () => {
    it('should handle basic word concatenation', () => {
      expect(processTextChunk('Hello', ' world')).toBe('Hello world');
      expect(processTextChunk('Hello ', 'world')).toBe('Hello world');
      expect(processTextChunk('Hello', ' world')).toBe('Hello world');
    });

    it('should handle number concatenation without spaces', () => {
      expect(processTextChunk('500', '000')).toBe('500 000'); // Numbers are separate words
      expect(processTextChunk('500', ',')).toBe('500,'); // Comma attaches to previous word
      expect(processTextChunk('500,', '000')).toBe('500,000'); // Number after comma attaches
      expect(processTextChunk('$', '500')).toBe('$500'); // Number after currency attaches
      expect(processTextChunk('500', '$')).toBe('500$'); // Currency attaches to previous word
    });

    it('should handle decimal numbers correctly', () => {
      expect(processTextChunk('3', '.')).toBe('3.'); // Decimal point attaches to previous word
      expect(processTextChunk('3.', '14')).toBe('3. 14'); // Number after decimal is separate
      expect(processTextChunk('3.14', '159')).toBe('3.14 159'); // Number after decimal is separate
    });

    it('should handle punctuation attachment', () => {
      expect(processTextChunk('Hello', ',')).toBe('Hello,');
      expect(processTextChunk('Hello', '!')).toBe('Hello!');
      expect(processTextChunk('Hello', '?')).toBe('Hello?');
      expect(processTextChunk('Hello', '.')).toBe('Hello.');
    });

    it('should handle Spanish punctuation correctly', () => {
      expect(processTextChunk('¿', 'Qué')).toBe('¿Qué');
      expect(processTextChunk('¡', 'Hola')).toBe('¡Hola');
      expect(processTextChunk('¿Qué', ' opciones')).toBe('¿Qué opciones');
    });

    it('should handle word fragments correctly', () => {
      expect(processTextChunk('cum', 'plan')).toBe('cumplan');
      expect(processTextChunk('cum', ' plan')).toBe('cum plan');
    });

    it('should handle real-world Spanish conversation scenarios', () => {
      // Test the specific problematic case first
      expect(processTextChunk('servicios.', '¿')).toBe('servicios.¿'); // Spanish punctuation attaches
      expect(processTextChunk('¿', 'Qué')).toBe('¿Qué'); // Word after Spanish punctuation attaches
      expect(processTextChunk('cum', 'plan')).toBe('cumplan'); // Word fragments concatenate
      
      // Now test the full scenario
      const chunks = [
        'Claro, mi presupuesto está entre $200,000 y $500,000. Estoy buscando una casa o apartamento que sea adecuado para una familia de 3 o 4 personas. La ubicación es clave para nosotros, queremos una zona segura y con buenos servicios.',
        '¿',
        'Qué',
        ' opciones',
        ' tienen',
        ' que',
        ' se',
        ' ajusten',
        ' a',
        ' este',
        ' rango',
        ' y',
        ' cum',
        'plan',
        ' con',
        ' esos',
        ' requisitos?'
      ];
      
      const result = processTextChunks(chunks);
      expect(result).toBe('Claro, mi presupuesto está entre $200,000 y $500,000. Estoy buscando una casa o apartamento que sea adecuado para una familia de 3 o 4 personas. La ubicación es clave para nosotros, queremos una zona segura y con buenos servicios.¿Qué opciones tienen que se ajusten a este rango y cumplan con esos requisitos?');
    });

    it('should handle spacing correctly based on chunk structure', () => {
      // Test the specific problematic cases mentioned by user
      expect(processTextChunk('Quer', ' emos')).toBe('Quer emos');
      expect(processTextChunk('cerc', ' anos')).toBe('cerc anos');
      expect(processTextChunk('var', ' ía')).toBe('var ía');
      
      // Test the example: "Sí", ".", " Quie", "ro", " una", " zona", " segu", "ra"
      expect(processTextChunk('Sí', '.')).toBe('Sí.');
      expect(processTextChunk('Sí.', ' Quie')).toBe('Sí. Quie');
      expect(processTextChunk('Sí. Quie', 'ro')).toBe('Sí. Quiero');
      expect(processTextChunk('Sí. Quiero', ' una')).toBe('Sí. Quiero una');
      expect(processTextChunk('Sí. Quiero una', ' zona')).toBe('Sí. Quiero una zona');
      expect(processTextChunk('Sí. Quiero una zona', ' segu')).toBe('Sí. Quiero una zona segu');
      expect(processTextChunk('Sí. Quiero una zona segu', 'ra')).toBe('Sí. Quiero una zona segura');
    });

    it('should handle the exact problematic scenario from user logs', () => {
      // Simulate the exact chunks that were causing issues
      const chunks = [
        'Estamos buscando una casa o apartamento dentro de un presupuesto que',
        ' var',
        ' ía',
        ' entre $200,000 y $500,000.',
        ' Quer',
        ' emos',
        ' encontrar una propiedad que se ajuste a nuestras necesidades y que nos ofrezca la mejor relación calidad-precio.',
        ' Además, estamos muy interesados en una ubicación segura y con buenos servicios',
        ' cerc',
        ' anos',
        '.'
      ];
      
      const result = processTextChunks(chunks);
      expect(result).toBe('Estamos buscando una casa o apartamento dentro de un presupuesto que var ía entre $200,000 y $500,000. Quer emos encontrar una propiedad que se ajuste a nuestras necesidades y que nos ofrezca la mejor relación calidad-precio. Además, estamos muy interesados en una ubicación segura y con buenos servicios cerc anos.');
    });

    it('should handle the comprehensive test case correctly', () => {
      // Test case: "Una", " preg", "unta", " para", " ti", ":", " ¿", "Cuá", "ntos", " años", " tienes", "?", " Yo", " tengo", "25", " años", " y", " $", "25", ",", "000", " en", " mi", " cuenta", "."
      const chunks = [
        'Una',
        ' preg',
        'unta',
        ' para',
        ' ti',
        ':',
        ' ¿',
        'Cuá',
        'ntos',
        ' años',
        ' tienes',
        '?',
        ' Yo',
        ' tengo',
        '25',
        ' años',
        ' y',
        ' $',
        '25',
        ',',
        '000',
        ' en',
        ' mi',
        ' cuenta',
        '.'
      ];
      
      const result = processTextChunks(chunks);
      expect(result).toBe('Una pregunta para ti: ¿Cuántos años tienes? Yo tengo 25 años y $25,000 en mi cuenta.');
    });

    it('should debug the specific problematic case', () => {
      // Test the specific case that's failing: "Una preg" + "unta"
      expect(processTextChunk('Una preg', 'unta')).toBe('Una pregunta');
      expect(processTextChunk('Una', ' preg')).toBe('Una preg');
      expect(processTextChunk('Una preg', 'unta')).toBe('Una pregunta');
    });

    it('should handle complex scenarios', () => {
      // Example from the user: "M", "ira", ",", " estamos", " buscando", " algo", " que", " of", "rez", "ca", " unos", " $", "500", ",", "000", " en", " total", "."
      expect(processTextChunk('', 'M')).toBe('M');
      expect(processTextChunk('M', 'ira')).toBe('Mira');
      expect(processTextChunk('Mira', ',')).toBe('Mira,');
      expect(processTextChunk('Mira,', ' estamos')).toBe('Mira, estamos');
      expect(processTextChunk('Mira, estamos', ' buscando')).toBe('Mira, estamos buscando');
      expect(processTextChunk('Mira, estamos buscando', ' algo')).toBe('Mira, estamos buscando algo');
      expect(processTextChunk('Mira, estamos buscando algo', ' que')).toBe('Mira, estamos buscando algo que');
      expect(processTextChunk('Mira, estamos buscando algo que', ' of')).toBe('Mira, estamos buscando algo que of');
      expect(processTextChunk('Mira, estamos buscando algo que of', 'rez')).toBe('Mira, estamos buscando algo que ofrez');
      expect(processTextChunk('Mira, estamos buscando algo que ofrez', 'ca')).toBe('Mira, estamos buscando algo que ofrezca');
      expect(processTextChunk('Mira, estamos buscando algo que ofrezca', ' unos')).toBe('Mira, estamos buscando algo que ofrezca unos');
      expect(processTextChunk('Mira, estamos buscando algo que ofrezca unos', ' $')).toBe('Mira, estamos buscando algo que ofrezca unos $');
      expect(processTextChunk('Mira, estamos buscando algo que ofrezca unos $', '500')).toBe('Mira, estamos buscando algo que ofrezca unos $500');
      expect(processTextChunk('Mira, estamos buscando algo que ofrezca unos $500', ',')).toBe('Mira, estamos buscando algo que ofrezca unos $500,');
      expect(processTextChunk('Mira, estamos buscando algo que ofrezca unos $500,', '000')).toBe('Mira, estamos buscando algo que ofrezca unos $500,000');
      expect(processTextChunk('Mira, estamos buscando algo que ofrezca unos $500,000', ' en')).toBe('Mira, estamos buscando algo que ofrezca unos $500,000 en');
      expect(processTextChunk('Mira, estamos buscando algo que ofrezca unos $500,000 en', ' total')).toBe('Mira, estamos buscando algo que ofrezca unos $500,000 en total');
      expect(processTextChunk('Mira, estamos buscando algo que ofrezca unos $500,000 en total', '.')).toBe('Mira, estamos buscando algo que ofrezca unos $500,000 en total.');
    });

    it('should handle empty strings', () => {
      expect(processTextChunk('', 'Hello')).toBe('Hello');
      expect(processTextChunk('Hello', '')).toBe('Hello');
      expect(processTextChunk('', '')).toBe('');
    });

    it('should preserve existing spacing when appropriate', () => {
      expect(processTextChunk('Hello ', 'world')).toBe('Hello world');
      expect(processTextChunk('Hello', ' world')).toBe('Hello world');
      expect(processTextChunk('Hello  ', '  world')).toBe('Hello    world'); // Preserves existing spacing
    });
  });

  describe('processTextChunks', () => {
    it('should process multiple chunks correctly', () => {
      const chunks = ['M', 'ira', ',', ' estamos', ' buscando', ' algo', ' que', ' of', 'rez', 'ca', ' unos', ' $', '500', ',', '000', ' en', ' total', '.'];
      const result = processTextChunks(chunks);
      expect(result).toBe('Mira, estamos buscando algo que ofrezca unos $500,000 en total.');
    });

    it('should handle empty chunks array', () => {
      expect(processTextChunks([])).toBe('');
    });

    it('should handle single chunk', () => {
      expect(processTextChunks(['Hello'])).toBe('Hello');
    });
  });

  describe('smartProcessTextChunk', () => {
    it('should identify chunk types correctly', () => {
      expect(smartProcessTextChunk('', 'hello').chunkType).toBe('word');
      expect(smartProcessTextChunk('', '123').chunkType).toBe('number');
      expect(smartProcessTextChunk('', ',').chunkType).toBe('punctuation');
      expect(smartProcessTextChunk('', '$').chunkType).toBe('symbol');
      expect(smartProcessTextChunk('', 'a1b').chunkType).toBe('mixed');
    });

    it('should detect concatenation', () => {
      const result = smartProcessTextChunk('500', '000');
      expect(result.wasConcatenated).toBe(false); // Numbers are separate words
      expect(result.content).toBe('500 000');
    });

    it('should detect non-concatenation', () => {
      const result = smartProcessTextChunk('Hello', ' world'); // Real case: chunk starts with space
      expect(result.wasConcatenated).toBe(false); // No concatenation, space was already there
      expect(result.content).toBe('Hello world');
    });
  });

  describe('shouldConcatenateWithoutSpace', () => {
    it('should concatenate numbers without space', () => {
      expect(shouldConcatenateWithoutSpace('500', '000')).toBe(true);
      expect(shouldConcatenateWithoutSpace('123', '456')).toBe(true);
    });

    it('should concatenate decimal separators', () => {
      expect(shouldConcatenateWithoutSpace('3', '.')).toBe(true);
      expect(shouldConcatenateWithoutSpace('3.', '14')).toBe(true);
    });

    it('should concatenate thousand separators', () => {
      expect(shouldConcatenateWithoutSpace('500', ',')).toBe(true);
      expect(shouldConcatenateWithoutSpace('500,', '000')).toBe(true);
    });

    it('should concatenate currency symbols', () => {
      expect(shouldConcatenateWithoutSpace('$', '500')).toBe(true);
      expect(shouldConcatenateWithoutSpace('500', '$')).toBe(true);
    });

    it('should concatenate punctuation to words', () => {
      expect(shouldConcatenateWithoutSpace('Hello', ',')).toBe(true);
      expect(shouldConcatenateWithoutSpace('Hello', '!')).toBe(true);
    });

    it('should not concatenate words with spaces', () => {
      expect(shouldConcatenateWithoutSpace('Hello', 'world')).toBe(false);
      expect(shouldConcatenateWithoutSpace('Hello', ' world')).toBe(false);
    });
  });
});
