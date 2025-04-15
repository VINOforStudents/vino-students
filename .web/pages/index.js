/** @jsxImportSource @emotion/react */


import { Fragment, useCallback, useContext, useRef } from "react"
import { Box as RadixThemesBox, Button as RadixThemesButton, Container as RadixThemesContainer, Flex as RadixThemesFlex, Text as RadixThemesText, TextField as RadixThemesTextField } from "@radix-ui/themes"
import { EventLoopContext, StateContexts, UploadFilesContext } from "$/utils/context"
import { DebounceInput } from "react-debounce-input"
import { Event, refs } from "$/utils/state"
import {  } from "react-dropzone"
import { useDropzone } from "react-dropzone"
import NextHead from "next/head"



export function Comp_6ed195c6e7c81364b7d78c0830607748 () {
  
  const ref_my_upload = useRef(null); refs["ref_my_upload"] = ref_my_upload;
  const [addEvents, connectErrors] = useContext(EventLoopContext);
  const [filesById, setFilesById] = useContext(UploadFilesContext);
  const on_drop_efb1646e227894bf574e6bf836c0ccee = useCallback(e => setFilesById(filesById => {
    const updatedFilesById = Object.assign({}, filesById);
    updatedFilesById["my_upload"] = e;
    return updatedFilesById;
  })
    , [addEvents, Event, filesById, setFilesById])
  const {getRootProps: hpzmdmgo, getInputProps: xoxelmrs}  = useDropzone(({ ["onDrop"] : on_drop_efb1646e227894bf574e6bf836c0ccee, ["multiple"] : true, ["id"] : "my_upload" }));





  
  return (
    <>

<RadixThemesBox className={"rx-Upload"} css={({ ["text"] : "Upload a file", ["width"] : "20%", ["marginTop"] : "1em", ["marginBottom"] : "1em", ["border"] : "1px dashed var(--accent-12)", ["padding"] : "5em", ["textAlign"] : "center" })} id={"my_upload"} ref={ref_my_upload} {...hpzmdmgo()}>

<input type={"file"} {...xoxelmrs()}/>
</RadixThemesBox>
</>
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

export function Box_44b97ca4c47754923fc2894850b22819 () {
  
  const reflex___state____state__vino_students___state____state = useContext(StateContexts.reflex___state____state__vino_students___state____state)





  
  return (
    <RadixThemesBox>

<>{ reflex___state____state__vino_students___state____state.chat_history.map((messages, index_24a3764f9ed187ce) => (
  <RadixThemesBox css={({ ["marginTop"] : "1em", ["marginBottom"] : "1em", ["width"] : "100%" })} key={index_24a3764f9ed187ce}>

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

export function Debounceinput_34d47963b3f03d69c2e036c53c9ca8e8 () {
  
  const reflex___state____state__vino_students___state____state = useContext(StateContexts.reflex___state____state__vino_students___state____state)
  const [addEvents, connectErrors] = useContext(EventLoopContext);


  const on_change_994401bfc05f073394175594a8d43ab8 = useCallback(((_e) => (addEvents([(Event("reflex___state____state.vino_students___state____state.set_question", ({ ["question"] : _e["target"]["value"] }), ({  })))], [_e], ({  })))), [addEvents, Event])



  
  return (
    <DebounceInput css={({ ["borderWidth"] : "1px", ["padding"] : "0.5em", ["boxShadow"] : "rgba(0, 0, 0, 0.15) 0px 2px 8px", ["width"] : "40em" })} debounceTimeout={300} element={RadixThemesTextField.Root} onChange={on_change_994401bfc05f073394175594a8d43ab8} placeholder={"Ask a question"} value={reflex___state____state__vino_students___state____state.question}/>
  )
}

export default function Component() {
    




  return (
    <Fragment>

<RadixThemesContainer css={({ ["padding"] : "16px", ["align"] : "center" })} size={"3"}>

<RadixThemesFlex align={"center"} className={"rx-Stack"} css={({ ["height"] : "100vh" })} direction={"column"} gap={"4"}>

<Box_44b97ca4c47754923fc2894850b22819/>
<RadixThemesFlex css={({ ["flex"] : 1, ["justifySelf"] : "stretch", ["alignSelf"] : "stretch" })}/>
<RadixThemesFlex align={"start"} className={"rx-Stack"} direction={"row"} gap={"3"}>

<Debounceinput_34d47963b3f03d69c2e036c53c9ca8e8/>
<Button_ab0170d6094145421d8a6ddcc4b3b4f7/>
</RadixThemesFlex>
<Comp_6ed195c6e7c81364b7d78c0830607748/>
</RadixThemesFlex>
</RadixThemesContainer>
<NextHead>

<title>

{"VinoStudents | Index"}
</title>
<meta content={"favicon.ico"} property={"og:image"}/>
</NextHead>
</Fragment>
  )
}
