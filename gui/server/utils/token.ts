import * as jose from "jose";

const config = useRuntimeConfig();
const jwtSecret = new TextEncoder().encode(config.jwtSecret);

interface TokenPayload {
  userId: string,
  isAdmin: boolean,
}

export async function createToken(userId: string, isAdmin: boolean = false): Promise<string> {

  const payload: TokenPayload = { userId, isAdmin };

  // generate token
  return await new jose.SignJWT(payload as any)
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setIssuer(config.jwtIssuer)
    .setAudience(config.jwtAudience)
    .setExpirationTime("8h")
    .sign(jwtSecret);
}

export async function verifyToken(token: string | undefined): Promise<TokenPayload> {

  if (!token) {
    throw createError({
      statusCode: 401,
      statusMessage: "Unauthorized",
    });
  }

  // check token
  try {
    const { payload } = await jose.jwtVerify(
      token,
      jwtSecret,
      {
        issuer: config.jwtIssuer,
        audience: config.jwtAudience,
      },
    );

    return {
      userId: payload.userId as string,
      isAdmin: payload.isAdmin as boolean,
    } as TokenPayload;
  } catch (error) {
    throw createError({
      statusCode: 401,
      statusMessage: "Unauthorized",
    });
  }
}
