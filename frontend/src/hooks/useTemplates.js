import { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Custom hook for loading SMS/WhatsApp templates
 * Prevents code duplication across components
 */
export const useTemplates = (channel) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTemplates();
  }, [channel]);

  const loadTemplates = async () => {
    if (!channel) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const endpoint = channel === 'sms' 
        ? '/api/sms/templates'
        : '/api/whatsapp/templates';
      
      const response = await axios.get(endpoint);
      const templateData = response.data.templates || {};
      
      // Convert to array format for easier rendering
      setTemplates(Object.entries(templateData));
    } catch (err) {
      console.error('Error loading templates:', err);
      setError(err.message);
      setTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  return { templates, loading, error, reload: loadTemplates };
};
