import { z } from "zod";

export const booleanQueryParam = z
  .enum(['true', 'false', '1', '0', 'on', 'off'])
  .optional()
  .transform((value) => {
    if (value === undefined) return false;
    return ['true', '1', 'on'].includes(value.toLowerCase());
  });
