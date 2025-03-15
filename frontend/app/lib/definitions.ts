import { z } from 'zod'
 
// Define the schema for the signup form, for data type validation

export const SignupFormSchema = z.object({
    username: z
        .string()
        .min(2, { message: 'Username must be at least 2 characters long.' })
        .trim(),
    full_name: z
        .string()
        .min(2, { message: 'Name must be at least 2 characters long.' })
        .trim(),
    email: z.string().email({ message: 'Please enter a valid email.' }).trim(),
    password: z
        .string()
        .min(2, { message: 'Be at least 2 characters long' })
        // .regex(/[a-zA-Z]/, { message: 'Contain at least one letter.' })
        // .regex(/[0-9]/, { message: 'Contain at least one number.' })
        // })
        .trim(),
})
 
export type FormState =
  | {
      errors?: {
        username?: string[]
        full_name?: string[]
        email?: string[]
        password?: string[]
      }
      message?: string
    }
  | undefined