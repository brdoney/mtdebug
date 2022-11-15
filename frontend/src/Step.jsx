import useSWR from "swr";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

export default function Step({...args}) {
    // render
    const { data : output, error } = useSWR("/api/step", fetcher, {refreshInterval:5});

    let message = { line:  "", num: -1};

    if (error) {
        return <div>
            <input disabled type="button" value="STEP" />
            <input disabled type="button" value="CONTINUE" />
            <input disabled type="button" value="STOP" />
            </div>;
    }

    if (output) 
    {
        console.log(output.line_num)
        if (output.line_num !== -1 ){
            message.line = output.curr_line;
            message.num = output.line_num
        } else{
            return(
                <code>Program not in execution</code>
            );
        }
    }

    return (
        <div className="Step">
            <header className="Step-info">
                <h1>Debug actions: </h1>
                <button name="submit" value="step">step</button>
                <button name="submit" value="continue">continue</button>
                <button name="submit" value="stop">stop</button>
                <p><code>{message.num + "\t" + message.line}</code></p>
            </header>
        </div> 
    );
}