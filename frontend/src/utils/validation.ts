import { ProjectDescription } from '../api/types';

interface ValidationResult {
    isValid: boolean;
    errors: string[];
}

export const validateProjectDescription = (description: ProjectDescription): ValidationResult => {
    const errors: string[] = [];

    // Validate description
    if (!description.description) {
        errors.push('Project description is required');
    } else if (description.description.length < 10) {
        errors.push('Project description must be at least 10 characters long');
    } else if (description.description.length > 1000) {
        errors.push('Project description must not exceed 1000 characters');
    }

    // Check for XSS attempts
    const xssPattern = /<[^>]*>|javascript:|data:/i;
    if (xssPattern.test(description.description)) {
        errors.push('Project description contains invalid characters');
    }

    // Validate requirements
    if (description.requirements.length > 10) {
        errors.push('Maximum 10 requirements allowed');
    }
    description.requirements.forEach(req => {
        if (!req.trim()) {
            errors.push('Requirements cannot be empty strings');
        } else if (req.length > 100) {
            errors.push('Each requirement must not exceed 100 characters');
        }
    });

    // Validate constraints
    if (description.constraints.length > 10) {
        errors.push('Maximum 10 constraints allowed');
    }
    description.constraints.forEach(constraint => {
        if (!constraint.trim()) {
            errors.push('Constraints cannot be empty strings');
        } else if (constraint.length > 100) {
            errors.push('Each constraint must not exceed 100 characters');
        }
    });

    return {
        isValid: errors.length === 0,
        errors
    };
}; 