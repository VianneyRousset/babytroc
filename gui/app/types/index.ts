import type { FetchError } from 'ofetch'
import type { VisibleArea } from 'vue-advanced-cropper'
import type { AsyncDataRequestStatus } from '#app'

export interface PaginatedSource<T> {
  data: Array<T>
  more: () => Promise<void>
  reset: () => void
  end: boolean
  error: FetchError | null
  status: AsyncDataRequestStatus
}

export type StudioImageCrop = VisibleArea

export type StudioImage = {
  id: number
  original: string
  width?: number
  height?: number
  maxWidth?: number
  crop: StudioImageCrop | undefined
  copy: () => StudioImage
  setCrop: (crop: StudioImageCrop) => void
  cropped?: string
}

export type MsgPlacement = ('auto' | 'auto-start' | 'auto-end' | 'top' | 'top-start' | 'top-end'
  | 'right' | 'right-start' | 'right-end' | 'bottom' | 'bottom-start' | 'bottom-end'
  | 'left' | 'left-start' | 'left-end')
