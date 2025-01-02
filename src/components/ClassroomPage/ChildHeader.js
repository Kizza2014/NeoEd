import "./ChildHeader.css"

function ChildHeader({nameHeader}) {
    return(
        <div style={{ backgroundColor: 'white', paddingTop:"30px"}}>
            <div className = "child-header-container">
                <h2 style={{margin:3}}>
                    {nameHeader}
                </h2>
            </div>
        </div>
    )
}

export default ChildHeader;