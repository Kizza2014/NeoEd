import "./ChildHeader.css"

function ChildHeader({nameHeader}) {
    return(
        <div className="header-container">
        <div className="child-header-container">
            <h2>{nameHeader}</h2>
        </div>
        </div>

    )
}

export default ChildHeader;