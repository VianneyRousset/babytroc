export type ImageSize = 128 | 256 | 512 | 1024;

export const imagePath = (name: string, size: ImageSize = 1024) =>
	`/images/${name}_${size}.webp`;
