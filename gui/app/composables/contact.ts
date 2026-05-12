export type ContactSubmit = {
	name: string;
	email: string;
	subject: string;
	message: string;
	capToken: string;
};

export function useSendContactMessage() {
	const { $api } = useNuxtApp();

	// No retry: cap tokens are single-use — retrying with the same token returns 400.
	const { mutateAsync: sendContactMessage, ...mutation } = useMutation({
		mutation: (ctx: ContactSubmit) => {
			return $api("/v1/utils/contact", {
				method: "POST",
				body: {
					name: ctx.name,
					email: ctx.email,
					subject: ctx.subject,
					message: ctx.message,
					cap_token: ctx.capToken,
					website: "", // honeypot — always empty; server rejects non-empty submissions
				},
			});
		},
	});

	return { sendContactMessage, ...mutation };
}
