/** @jsxImportSource @emotion/react */


import { Fragment, useCallback, useContext, useRef } from "react"
import { Box as RadixThemesBox, Button as RadixThemesButton, Container as RadixThemesContainer, Flex as RadixThemesFlex, Spinner as RadixThemesSpinner, Text as RadixThemesText, TextField as RadixThemesTextField } from "@radix-ui/themes"
import { EventLoopContext, StateContexts } from "$/utils/context"
import { Event, isTrue, refs } from "$/utils/state"
import { DebounceInput } from "react-debounce-input"
import {  } from "react-dropzone"
import { useDropzone } from "react-dropzone"
import NextHead from "next/head"



export function Comp_54837a0141f48adff46ce59712f2490c () {
  
  const ref_my_upload = useRef(null); refs["ref_my_upload"] = ref_my_upload;
  const [addEvents, connectErrors] = useContext(EventLoopContext);
  const on_drop_568044fd82f65ffaf715a8edfab50180 = useCallback(((_files) => (addEvents([(Event("reflex___state____state.vino_students___state____state.handle_upload", ({ ["files"] : _files, ["upload_id"] : "default" }), ({  }), "uploadFiles"))], [_files], ({  })))), [addEvents, Event])
  const {getRootProps: fqktnhja, getInputProps: fmbubgqc}  = useDropzone(({ ["onDrop"] : on_drop_568044fd82f65ffaf715a8edfab50180, ["multiple"] : true, ["id"] : "my_upload" }));





  
  return (
    <>

<RadixThemesBox className={"rx-Upload"} css={({ ["border"] : "1px dotted rgb(107,114,128)", ["padding"] : "2em", ["width"] : "40em", ["marginTop"] : "1em", ["marginBottom"] : "1em", ["textAlign"] : "center" })} id={"my_upload"} ref={ref_my_upload} {...fqktnhja()}>

<input type={"file"} {...fmbubgqc()}/>
<RadixThemesFlex align={"start"} className={"rx-Stack"} direction={"column"} gap={"3"}>

<RadixThemesButton>

{"Select File(s)"}
</RadixThemesButton>
<RadixThemesText as={"p"}>

{"Drag and drop files here or click to select files."}
</RadixThemesText>
</RadixThemesFlex>
</RadixThemesBox>
</>
  )
}

export function Debounceinput_34d47963b3f03d69c2e036c53c9ca8e8 () {
  
  const reflex___state____state__vino_students___state____state = useContext(StateContexts.reflex___state____state__vino_students___state____state)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_change_994401bfc05f073394175594a8d43ab8 = useCallback(((_e) => (addEvents([(Event("reflex___state____state.vino_students___state____state.set_question", ({ ["question"] : _e["target"]["value"] }), ({  })))], [_e], ({  })))), [addEvents, Event])



  
  return (
    <DebounceInput css={({ ["borderWidth"] : "1px", ["padding"] : "0.5em", ["boxShadow"] : "rgba(0, 0, 0, 0.15) 0px 2px 8px", ["width"] : "40em" })} debounceTimeout={300} element={RadixThemesTextField.Root} onChange={on_change_994401bfc05f073394175594a8d43ab8} placeholder={"Ask a question"} value={reflex___state____state__vino_students___state____state.question}/>
  )
}

export function Button_dc04a795abc5b69ec44abbd2a1f66d6f () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_f0568120a61bc55578f1ef5a2031d391 = useCallback(((...args) => (addEvents([(Event("reflex___state____state.vino_students___state____state.clear_chat_history", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    <RadixThemesButton color={"red"} css={({ ["position"] : "fixed", ["top"] : "1em", ["right"] : "1em", ["zIndex"] : "999" })} onClick={on_click_f0568120a61bc55578f1ef5a2031d391} size={"2"} variant={"outline"}>

{"Clear History"}
</RadixThemesButton>
  )
}

export function Fragment_58d58690c875c13baba1437584e84b51 () {
  
  const reflex___state____state__vino_students___state____state = useContext(StateContexts.reflex___state____state__vino_students___state____state)





  
  return (
    <Fragment>

{reflex___state____state__vino_students___state____state.is_loading ? (
  <Fragment>

<RadixThemesSpinner size={"2"}/>
</Fragment>
) : (
  <Fragment>

<RadixThemesText as={"p"} css={({ ["color"] : "red", ["marginTop"] : "0.5em", ["display"] : (!((reflex___state____state__vino_students___state____state.error_message === "")) ? "block" : "none") })}>

{reflex___state____state__vino_students___state____state.error_message}
</RadixThemesText>
</Fragment>
)}
</Fragment>
  )
}

export function Box_44706e436e7f2851bf143257c12e7918 () {
  
  const reflex___state____state__vino_students___state____state = useContext(StateContexts.reflex___state____state__vino_students___state____state)





  
  return (
    <RadixThemesBox>

<>{ reflex___state____state__vino_students___state____state.chat_history.map((messages, index_894ba3a046b25245) => (
  <RadixThemesBox css={({ ["marginTop"] : "1em", ["marginBottom"] : "1em", ["width"] : "100%" })} key={index_894ba3a046b25245}>

<RadixThemesBox css={({ ["textAlign"] : "right" })}>

<RadixThemesText as={"p"} css={({ ["padding"] : "1em", ["borderRadius"] : "5px", ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em", ["boxShadow"] : "rgba(0, 0, 0, 0.15) 0px 2px 8px", ["maxWidth"] : "40em", ["display"] : "inline-block", ["marginLeft"] : "20%", ["backgroundColor"] : "var(--gray-4)" })}>

{messages.at(0)}
</RadixThemesText>
</RadixThemesBox>
<RadixThemesBox css={({ ["textAlign"] : "left" })}>

<RadixThemesText as={"p"} css={({ ["padding"] : "1em", ["borderRadius"] : "5px", ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em", ["boxShadow"] : "rgba(0, 0, 0, 0.15) 0px 2px 8px", ["maxWidth"] : "40em", ["display"] : "inline-block", ["marginRight"] : "20%", ["backgroundColor"] : "var(--cyan-8)" })}>

{messages.at(1)}
</RadixThemesText>
</RadixThemesBox>
</RadixThemesBox>
))}</>
</RadixThemesBox>
  )
}

export function Button_ab0170d6094145421d8a6ddcc4b3b4f7 () {
  
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_click_1500b56a8c097328485ce3ead669564f = useCallback(((...args) => (addEvents([(Event("reflex___state____state.vino_students___state____state.answer", ({  }), ({  })))], args, ({  })))), [addEvents, Event])



  
  return (
    <RadixThemesButton css={({ ["backgroundColor"] : "var(--accent-10)", ["boxShadow"] : "rgba(0, 0, 0, 0.15) 0px 2px 8px" })} onClick={on_click_1500b56a8c097328485ce3ead669564f}>

{"Send"}
</RadixThemesButton>
  )
}

export default function Component() {
    




  return (
    <Fragment>

<RadixThemesBox css={({ ["width"] : "100%" })}>

<Button_dc04a795abc5b69ec44abbd2a1f66d6f/>
<RadixThemesContainer css={({ ["padding"] : "16px" })} size={"3"}>

<RadixThemesFlex align={"center"} className={"rx-Stack"} css={({ ["height"] : "100vh" })} direction={"column"} gap={"4"}>

<Box_44706e436e7f2851bf143257c12e7918/>
<RadixThemesFlex css={({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })}/>
<RadixThemesFlex align={"start"} className={"rx-Stack"} direction={"row"} gap={"3"}>

<Debounceinput_d14b5dccd36bca94038dff934954cf5b/>
<Button_ab0170d6094145421d8a6ddcc4b3b4f7/>
</RadixThemesFlex>
<Comp_54837a0141f48adff46ce59712f2490c/>
<Fragment_58d58690c875c13baba1437584e84b51/>
</RadixThemesFlex>
</RadixThemesContainer>
</RadixThemesBox>
<NextHead>

<title>

{"VinoStudents | Index"}
</title>
<meta content={"favicon.ico"} property={"og:image"}/>
</NextHead>
</Fragment>
  )
}
