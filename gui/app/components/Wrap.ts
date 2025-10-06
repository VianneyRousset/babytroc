import { ShapeFlags } from '@vue/shared'
import { cloneVNode, type VNode, defineComponent } from 'vue'

function findLeaves(
  vnode: VNode,
  cb: (v: VNode) => void,
): void {
  // If children is an array, recurse, otherwise pass vnode to callback
  if (Array.isArray(vnode.children)) {
    vnode.children.forEach((child) => {
      if (typeof child === 'object' && child !== null) {
        findLeaves(child as VNode, cb)
      }
    })
  }
  else {
    cb(vnode)
  }
}

export default defineComponent({
  name: 'Wrap',
  props: {
    wrap: {
      type: Boolean,
      default: true,
    },
  },
  setup(props, { slots }) {
    if (!props.wrap)
      return () => slots.default?.()

    const wrapper = (slots.wrapper?.() ?? []).map(vnode => cloneVNode(vnode))

    findLeaves({ children: wrapper } as VNode, (vnode) => {
      vnode.shapeFlag = ShapeFlags.ARRAY_CHILDREN | ShapeFlags.ELEMENT
      if (!vnode.children || !Array.isArray(vnode.children)) {
        vnode.children = []
      }
      vnode.children.push(...(slots.default?.() ?? []))
    })

    return () => wrapper
  },
})
